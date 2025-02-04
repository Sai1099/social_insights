from files import app, main_users, profile
from flask import session, redirect, render_template, request, url_for, jsonify
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bson import json_util
import json
from datetime import datetime
from files.scrapper import facebook_login, visit_facebook_profile, scrape_page
from os import environ as env
import os


# Helper function to parse MongoDB results
def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/page/<username>', methods=['GET'])
def get_page_details(username):
    
    page_data = profile.find_one({"page_url": username})
    
    if not page_data:
        try:
            driver = webdriver.Chrome()
           
            username = os.getenv('USERNAME')
            password = os.getenv('PASSWORD')
            facebook_login(driver, username, password)
            page_url = visit_facebook_profile(driver, username)
            
            if page_url:
                details = scrape_page(driver, page_url)
                if details:
                 
                    details['created_at'] = datetime.now()
                    profile.insert_one(details)
                    page_data = details
                else:
                    return jsonify({"error": "Failed to scrape page"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            driver.quit()
    
    return jsonify(parse_json(page_data))

@app.route('/api/pages', methods=['GET'])
def get_pages():

    min_followers = request.args.get('min_followers', type=int)
    max_followers = request.args.get('max_followers', type=int)
    category = request.args.get('category')
    name = request.args.get('name')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    
    query = {}
    if min_followers and max_followers:
        query['followers'] = {'$gte': min_followers, '$lte': max_followers}
    if category:
        query['page_info'] = {'$regex': category, '$options': 'i'}
    if name:
        query['page_name'] = {'$regex': name, '$options': 'i'}
    
    skip = (page - 1) * per_page

    results = profile.find(query).skip(skip).limit(per_page)
    total = profile.count_documents(query)
 
    pages_data = list(results)
    response = {
        "pages": parse_json(pages_data),
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }
    
    return jsonify(response)

@app.route('/api/page/<username>/posts', methods=['GET'])
def get_page_posts(username):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    page_data = profile.find_one({"page_url": username})
    if not page_data or 'posts' not in page_data:
        return jsonify({"error": "Page or posts not found"}), 404
    

    start = (page - 1) * per_page
    end = start + per_page
    posts = page_data['posts'][start:end] if 'posts' in page_data else []
    
    response = {
        "posts": posts,
        "page": page,
        "per_page": per_page,
        "total_posts": len(page_data['posts']) if 'posts' in page_data else 0
    }
    
    return jsonify(response)

@app.route('/api/page/<username>/followers', methods=['GET'])
def get_page_followers(username):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    

    page_data = profile.find_one({"page_url": username})
    if not page_data or 'followers_list' not in page_data:
        return jsonify({"error": "Page or followers not found"}), 404

    start = (page - 1) * per_page
    end = start + per_page
    followers = page_data['followers_list'][start:end] if 'followers_list' in page_data else []
    
    response = {
        "followers": followers,
        "page": page,
        "per_page": per_page,
        "total_followers": len(page_data['followers_list']) if 'followers_list' in page_data else 0
    }
    
    return jsonify(response)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
