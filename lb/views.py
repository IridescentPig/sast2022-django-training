from email.policy import strict
from re import sub
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from pip import main
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method
import time

def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })

# TODO: Add HTTP method check
@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, username: str):
    # TODO: Complete `/history/<slug:username>` API
    res = Submission.objects.filter(user__username = username).order_by('time')
    if res.first():
        return JsonResponse([
            {
                **model_to_dict(submisson, exclude = ['id', 'user', 'avatar'])
            }
            for submisson in res
        ], safe = False)
    else:
        return JsonResponse({
            'code': -1
        }, status = 404)
    #raise NotImplementedError


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    # TODO: Complete `/submit` API
    try:
        req_json = json.loads(req.body, strict = False)
        if 'user' in req_json and 'avatar' in req_json and 'content' in req_json:
            if len(req_json['user']) > 255:
                return JsonResponse({
                    'code': -1,
                    'msg': '用户名太长了'
                })
            if len(req_json['avatar']) > 1e5:
                return JsonResponse({
                    'code': -2,
                    'msg': '图像太大了'
                })
            try:
                main_score, subs = utils.judge(req_json['content'])
            except:
                return JsonResponse({
                    'code': -3,
                    'msg': '提交内容非法呜呜'
                })
            submit_user = User.objects.filter(username = req_json['user']).first()
            if submit_user:
                pass
            else:
                User.objects.create(username = req_json['user'])
                submit_user = User.objects.filter(username = req_json['user']).first()
            subs_str = ','.join([str(i) for i in subs])
            Submission.objects.create(user = submit_user, avatar = req_json['avatar'], time = time.time(), score = main_score, subs = subs_str)
            return JsonResponse({
                'code': 0,
                'msg': '提交成功',
                'data': {
                    'leaderboard': utils.get_leaderboard()
                }
            })
        else:
            return JsonResponse({
                'code': 1,
                'msg': '参数不全啊'
            })
    except:
        return JsonResponse({
            'code': -4,
            'msg': '提交内容非法'
        })
    #raise NotImplementedError


@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })
    try:
        req_json = json.loads(req.body, strict = False)
        if 'user' in req_json:
            vote_user = User.objects.filter(username = req_json['user']).first()
            if vote_user:
                vote_user.votes = F('votes') + 1
                vote_user.save()
                return JsonResponse({
                    'code': 0,
                    'data': {
                        'leaderboard': utils.get_leaderboard()
                    }
                })
            else:
                return JsonResponse({
                    'code': -1,
                })
        else:
            return JsonResponse({
                'code': -1,
            })
    except:
        return JsonResponse({
            'code': -1,
        })
    # TODO: Complete `/vote` API

    raise NotImplementedError
