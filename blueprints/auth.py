from flask import Blueprint, redirect, url_for

auth = Blueprint('authentication_blueprint', __name__)

@auth.route('/logout')
def logout():
    # Implémentez ici la logique de déconnexion
    return redirect(url_for('home'))
