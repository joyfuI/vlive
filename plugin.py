# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback

# third-party
from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import login_required

# sjva 공용
from framework.logger import get_logger
from framework import scheduler, socketio

# 패키지
package_name = __name__.split('.')[0]
logger = get_logger(package_name)
from .logic import Logic
from .logic_normal import LogicNormal
from .logic_queue import LogicQueue
from .model import ModelSetting

#########################################################
# 플러그인 공용
#########################################################
blueprint = Blueprint(package_name, package_name, url_prefix='/%s' % package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

menu = {
    'main': [package_name, 'V LIVE'],
    'sub': [
        ['setting', '설정'], ['scheduler', '스케줄링'], ['log', '로그']
    ],
    'category': 'vod'
}

plugin_info = {
    'version': '0.1.3',
    'name': 'vlive',
    'category_name': 'vod',
    'developer': 'joyfuI',
    'description': 'V LIVE 다운로드',
    'home': 'https://github.com/joyfuI/vlive',
    'more': ''
}

def plugin_load():
    Logic.plugin_load()
    # LogicQueue.queue_load()

def plugin_unload():
    Logic.plugin_unload()

#########################################################
# WEB Menu
#########################################################
@blueprint.route('/')
def home():
    return redirect('/%s/scheduler' % package_name)

@blueprint.route('/<sub>')
@login_required
def first_menu(sub):
    try:
        arg = {'package_name': package_name}

        if sub == 'setting':
            arg.update(ModelSetting.to_dict())
            arg['scheduler'] = str(scheduler.is_include(package_name))
            arg['is_running'] = str(scheduler.is_running(package_name))
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'scheduler':
            arg['save_path'] = ModelSetting.get('default_save_path')
            arg['filename'] = ModelSetting.get('default_filename')
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'log':
            return render_template('log.html', package=package_name)
    except Exception as e:
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())
    return render_template('sample.html', title='%s - %s' % (package_name, sub))

#########################################################
# For UI
#########################################################
@blueprint.route('/ajax/<sub>', methods=['POST'])
@login_required
def ajax(sub):
    logger.debug('AJAX %s %s', package_name, sub)
    try:
        # 공통 요청
        if sub == 'setting_save':
            ret = ModelSetting.setting_save(request)
            return jsonify(ret)

        elif sub == 'scheduler':
            go = request.form['scheduler']
            logger.debug('scheduler:%s', go)
            if go:
                Logic.scheduler_start()
            else:
                Logic.scheduler_stop()
            return jsonify(go)

        elif sub == 'one_execute':
            ret = Logic.one_execute()
            return jsonify(ret)

        # elif sub == 'reset_db':
        #     ret = Logic.reset_db()
        #     return jsonify(ret)

        # UI 요청
        # elif sub == 'analysis':
        #     url = request.form['url']
        #     ret = LogicNormal.analysis(url)
        #     return jsonify(ret)

        # elif sub == 'add_download':
        #     ret = LogicNormal.download(request.form)
        #     return jsonify(ret)

        elif sub == 'list_scheduler':
            ret = LogicNormal.get_scheduler()
            return jsonify(ret)

        elif sub == 'add_scheduler':
            ret = LogicNormal.add_scheduler(request.form)
            return jsonify(ret)

        elif sub == 'del_scheduler':
            ret = LogicNormal.del_scheduler(request.form['id'])
            return jsonify(ret)

        # elif sub == 'del_archive':
        #     LogicNormal.del_archive(request.form['id'])
        #     return jsonify([])
    except Exception as e:
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())

#########################################################
# socketio
#########################################################
def socketio_emit(cmd, data):
    socketio.emit(cmd, data, namespace='/%s' % package_name, broadcast=True)
