"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url
from . models import get_user_email

url_signer = URLSigner(session)

# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():


    add_post = URL('add_post', signer=url_signer)
    delete_post_url = URL('delete_post', signer=url_signer)
    rating_url = URL('add_thumbs', signer=url_signer)
    get_likers_url = URL('get_likers', signer=url_signer)


    return dict(
        # This is an example of a signed URL for the callback.
        get_posts_url = URL('get_posts', signer=url_signer),
        # Add other callbacks here.
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name"),
        add_post_url = add_post,
        delete_post_url=delete_post_url,
        rating_url=rating_url,
        likers_url=get_likers_url
    )

@action('get_posts')
@action.uses(url_signer.verify(), auth.user)
def get_posts():
    # Complete.
    posts = [] # Just to keep code from breaking.
    postData = db(db.post).select().as_list()

    for post in postData:
        email = post['user_email']

        r = db(db.auth_user.email == email).select().first()
        name = r.first_name + " " + r.last_name if r is not None else "Unknown"
        post["name"] = name

        thumbs = db((db.thumb.post_id == post.get('id')) & (db.thumb.user_email == email)).select().as_list()

        if len(thumbs) > 0:
            thumb = thumbs[0]
            post['rating'] = thumb
        else:
            post['rating'] = {'rating': -1}

    
    return dict(posts=postData)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), auth.user)
def add_post():
    data = request.json 

    id = db.post.insert(post_text=data.get('postText'))
    return dict(id=id) # You need to fill this in.

# Complete.

@action('delete_post', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def delete_post():
    jsonData = request.json

    postID = jsonData['postID']

    db(db.post.id == postID).delete()

    return dict()


@action('add_thumbs', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def add_thumbs():
    data = request.json
    current_rating = data['rating']
    post_id = data['id']
    current_email = get_user_email()

    isRated = False

    result = db((db.thumb.post_id == post_id) & (db.thumb.user_email == current_email)).select().first()

    if result is not None:
        isRated = True
    
    if not current_rating == -1:
        if isRated:
            db(db.thumb.id == result.id).update(rating=current_rating)
        else:
            db.thumb.insert(post_id=post_id, user_email=current_email, rating=current_rating)
             
    else:
        db(db.thumb.id == result.id).delete()

    return dict(data=current_email)


@action('get_likers', method="POST")
@action.uses(url_signer.verify(), auth.user, db)
def get_likers():
    data = request.json

    post_id = data.get("post_id")

    likers = db(db.thumb.post_id == post_id).select().as_list()

    likersList = []
    dislikersList = []

    for l in likers:
        r = db(db.auth_user.email == l.user_email).select().first()
        name = r.first_name + " " + r.list_name if r is not None else "Unknown"

        if l.get('rating') == 1:
            likersList.append(name)
        else:
            dislikersList.append(name)

        ratingValue = l.rating

    return dict()