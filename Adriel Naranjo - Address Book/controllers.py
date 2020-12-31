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

# used for signing delete button and form
url_signer = URLSigner(session)


def validateContact(form):
    firstName = form.vars['first_name']
    lastName = form.vars['last_name']

    if firstName is None: 
        form.errors['first_name'] = T('Enter first name')
    if lastName is None: 
        form.errors['last_name'] = T('Enter last name')


def validatePhone(form):
    phoneNumber = form.vars['phone_number']
    kind = form.vars['kind']
    if phoneNumber is None:
        form.errors['phone_number'] = T("Enter phone number")
    if kind is None:
        form.errors['kind'] = T("Enter the kind of phone")


# The auth.user restricts login to users only 
@action('index')
@action.uses(db, auth.user, session, 'index.html')
def index():
    # load contacts according to user_email 
    user_email = auth.current_user.get('email')
    contacts = db(db.contacts.user_email == user_email).select()

    # havent implimented into index yet 
    for contact in contacts:
        phoneNumbers = db(db.phone.contact_id == contact.id).select()
        
        phoneList = []
        for phone in phoneNumbers:
            phoneList.append("{0} ({1})".format(phone.phone_number, phone.kind))

        phoneString = ", ".join(phoneList)

        contact['p'] = phoneString


    # return the contacts and keep it signed
    return dict(c=contacts, s=url_signer)




@action('add_contact', method=['GET','POST'])
@action.uses('add_contact.html', session)
def add_contact():
    # since we are adding a contact to the database, we need to create a
    # form that will go into db.contacts and that form will keep the session
    # we are currently have cookies for and will use Bulma for styling the form
    form = Form(db.contacts, csrf_session=session, formstyle=FormStyleBulma, validation=validateContact)
    if form.accepted:
        # accepted the new table entry and redirect back to index to display
        # the new form that was added to the db contacts dict
        redirect(URL('index'))
    return dict(form=form)





@action('edit_contact/<contactID>', method=['GET', 'POST'])
@action.uses('add_contact.html', session, db)
def edit_contact(contactID = None):

    auth_user = auth.current_user
    email = auth_user.get('email')

    #form = None

    contacts = db((db.contacts.user_email == email) & (db.contacts.id == contactID)).select()
    
    if len(contacts) == 0:
        redirect(URL('index'))

    # set all these DAL attributes to the form we are pulling up to 
    # edit. 
    form = Form(db.contacts, record=contactID, deletable=False, csrf_session=session, formstyle=FormStyleBulma, validation=validateContact)
    if form.accepted:
        # accepted the new table edit and redirect back to index to display
        # the editted form that was in the db contacts dict
        redirect(URL('index'))

        
    return dict(form=form)



@action('add_phone/<contact_id>', method=['GET', "POST"])
@action.uses('add_phone.html', session)
def add_phone(contact_id=None):

    contacts = db(db.contacts.id == contact_id).select()
    
    contact = contacts[0]

    form = Form(db.phone, csrf_session=session, formstyle=FormStyleBulma, validation=validatePhone)
    if form.accepted:

        phoneID = form.vars['id']

        db(db.phone.id == phoneID).update(contact_id=contact_id)

        redirect(URL('edit_phone', contact_id))

    return dict(form=form, name = contact.first_name + " " + contact.last_name)



@action('delete_contact', method=['GET', 'POST'])
@action.uses('index.html', db, session, url_signer.verify())
def delete_contact():
    # request the paramaters from py4web db 
    parameters = request.params
    # access desired parameter - contact_id
    contact_id = parameters.get('contact_id', None)
    # delete contact_id associated with the button that is clicked
    db(db.contacts.id == contact_id).delete()
    redirect(URL('index'))


@action('edit_phone/<contactID>', method=['GET', 'POST'])
@action.uses('edit_phone.html', session, db)
def edit_phone(contactID = None):
    contacts = db(db.contacts.id == contactID).select()

    contact = contacts[0]

    phoneNumbers = db(db.phone.contact_id == contactID).select()

    return dict(contact_id = contactID, name = contact.first_name + " " + contact.last_name, phoneNumbers=phoneNumbers, signer = url_signer)


#I havent implimented on the add_phone.html side yet
@action('edit_phone_number/<phoneID>', method=['GET', 'POST'])
@action.uses('add_phone.html', session, db)
def edit_phone_number(phoneID=None):

    phoneList = db(db.phone.id == phoneID).select()

    if len(phoneList) == 0:
        redirect(URL('index'))

    contact_id = phoneList[0].contact_id

    contactList = db(db.contacts.id == contact_id).select()

    contactRow = contactList[0]

    auth_user = auth.current_user
    userEmail = auth_user.get('email')

    contacts = db((db.contacts.user_email == userEmail) & (db.contacts.id == contact_id)).select()

    form = Form(db.phone, deletable=False, record=phoneID, csrf_session=session, formstyle=FormStyleBulma, validation=validatePhone)

    if len(contacts) == 0:
        redirect(URL('edit_phone', str(contact_id)))

    if form.accepted:
        redirect(URL('edit_phone', str(contact_id)))

    return dict(form=form, name=contactRow.first_name + " " + contactRow.last_name)


@action('delete_phone', method =['GET', 'POST'])
@action.uses('edit_phone.html', db, session, url_signer.verify())
def delete_phone():
    phoneID = request.params.get('phoneID')
    contactID = request.params.get('contactID')

    db(db.phone.id == phoneID).delete()
    redirect(URL('edit_phone', str(contactID)))