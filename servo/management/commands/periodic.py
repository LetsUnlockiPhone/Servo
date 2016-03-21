# -*- coding: utf-8 -*-

import os
import sys
import gsxws
import subprocess
from time import strftime
from django.conf import settings
from django.core.cache import caches
from django.core.management.base import BaseCommand

from servo.models import GsxAccount, Article


class Command(BaseCommand):
    help = 'Peforms periodic commands'
    VERBS = ('comptia', 'articles',)

    def add_arguments(self, parser):
        parser.add_argument('verb', type=str, choices=self.VERBS, help='Periodic command to perform')

    def handle(self, *args, **options):
        try:
            act = GsxAccount.fallback()
        except Exception as e:
            print >> sys.stderr, 'Failed to connect to GSX (%s)' % e
            sys.exit(-1)

        if 'articles' in options['verb']: # Update GSX articles
            articles = gsxws.comms.fetch()
            for a in articles:
                try:
                    article = Article.from_gsx(a)
                    try:
                        content = gsxws.comms.content(article.gsx_id)
                        article.content = content.articleContent
                    except Exception as e:
                        pass
                    article.save()
                except ValueError as e:
                    pass

        if 'comptia' in options['verb']: # Update raw CompTIA data (all product groups)
            try:
                codes = gsxws.comptia.fetch()
                caches['comptia'].set('codes', codes)
            except Exception as e:
                print >> sys.stderr, 'Failed to fetch CompTIA codes (%s)' % e
                sys.exit(-1)

        exit(0)
