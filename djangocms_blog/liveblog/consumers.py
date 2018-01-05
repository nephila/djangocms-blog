# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json

from channels import Group

from djangocms_blog.models import Post


def liveblog_connect(message, apphook, lang, post):
    """
    Connect users to the group of the given post according to the given language

    Return with an error message if a post cannot be found

    :param message: channel connect message
    :param apphook: apphook config namespace
    :param lang: language
    :param post: post slug
    """
    try:
        post = Post.objects.namespace(apphook).language(lang).active_translations(slug=post).get()
    except Post.DoesNotExist:
        message.reply_channel.send({
            'text': json.dumps({'error': 'no_post'}),
        })
        return
    Group(post.liveblog_group).add(message.reply_channel)
    message.reply_channel.send({"accept": True})


def liveblog_disconnect(message, apphook, lang, post):
    """
    Disconnect users to the group of the given post according to the given language

    Return with an error message if a post cannot be found

    :param message: channel connect message
    :param apphook: apphook config namespace
    :param lang: language
    :param post: post slug
    """
    try:
        post = Post.objects.namespace(apphook).language(lang).active_translations(slug=post).get()
    except Post.DoesNotExist:
        message.reply_channel.send({
            'text': json.dumps({'error': 'no_post'}),
        })
        return
    Group(post.liveblog_group).discard(message.reply_channel)
