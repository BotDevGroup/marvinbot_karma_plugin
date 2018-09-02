from flask import Blueprint, render_template
from karma_plugin import KarmaPlugin

karma_app = Blueprint('karma_plugin', __name__, template_folder='templates')


@karma_app.route('/<chat_id>', methods=['GET'])
def karmareport(chat_id):
    return render_template('karmareport.html', report=KarmaPlugin.get_karma_report(int(chat_id)))
