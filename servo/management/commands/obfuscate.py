# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

from random import choice
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError

from servo.models import Customer, Order, User, Location, GsxAccount


class Command(BaseCommand):
    def handle(self, *args, **options):
        help = "Obfuscates the information in this Servo install"
        names = ('Daniel Scott', 'Amy Collins', 'Linda Moore',
            'Dennis Parker', 'Mark Cox', 'Jesse Clark',
            'Brian Patterson', 'Andrew Bennett', 'Frank Lopez',
            'Benjamin Wood', 'Michelle Jenkins', 'Alice Lee',
            'Lois Gonzales', 'Diane Perez', 'Cheryl Torres',
            'Ernest Smith', 'Steve Mitchell', 'Barbara Jones',
            'Wanda Roberts', 'Julie Watson', 'Carlos Harris',
            'Anthony Phillips', 'Ralph Gray', 'Donna Hill',
            'Alan Coleman', 'Lawrence Ross', 'Stephen Flores',
            'Robert Simmons', 'Gloria White', 'Doris Wilson', 
            'Shirley Sanders', 'Matthew Bell', 'Janice Hughes',
            'Walter Nelson', 'Gerald Taylor', 'Tammy Martin',
            'Gregory Barnes', 'Jonathan Baker', 'Lillian Green',
            'Brenda Hernandez', 'Denise Davis', 'Bobby Rogers',
            'Joe Lewis', 'Teresa Bailey', 'Craig Russell',
            'Angela Rivera', 'Rebecca Jackson', 'Nicole Henderson',
            'Kenneth James', 'Nicholas Bryant', 'Anne Washington',
            'Irene Miller', 'Theresa Martinez', 'Evelyn Sanchez',
            'Richard Anderson', 'Jeffrey Robinson', 'Heather Diaz',
            'Joshua Butler', 'Joan Peterson', 'Todd Campbell',
            'Timothy Kelly', 'Steven King', 'Norma Reed',
            'Carolyn Turner', 'Ruth Evans', 'Carol Thomas',
            'Arthur Howard', 'Peter Carter', 'Debra Ramirez',
            'Marie Walker', 'Donald Garcia', 'Janet Gonzalez',
            'Harold Adams', 'Bonnie Cook', 'Paula Long',
            'Bruce Griffin', 'Adam Hall' ,'Annie Young',
            'Jacqueline Alexander', 'Kimberly Edwards', 'Sarah Wright',
            'Terry Williams', 'Johnny Morris', 'Andrea Ward',
            'Margaret Allen', 'Sandra Price', 'Scott Foster',
            'Elizabeth Brown', 'Wayne Cooper', 'Mildred Brooks',
            'Dorothy Perry', 'Lori Powell', 'Kathryn Murphy',
            'Judy Johnson', 'Albert Morgan', 'William Richardson',
            'Randy Stewart', 'Roger Thompson', 'Anna Rodriguez',
        )
        """
        print 'Munging customer names of open orders...'
        for i in Order.objects.filter(state=Order.STATE_QUEUED):
            if i.customer:
                i.customer.name = choice(names)
                i.customer.save()
        """
        print 'Munging technician names'
        users = User.objects.exclude(username='filipp')
        newnames = [x.split()[0].lower() for x in names]
        oldnames = users.values_list("username", flat=True)
        idx = 0

        for i in users:
            i.first_name, i.last_name = choice(names).split()
            i.email = i.username + '@example.com'
            i.save()

        print 'Munging location names'
        a = 65
        for i in Location.objects.all():
            #i.title = 'Location %s' % chr(a)
            i.email = slugify(i.title) + '@example.com'
            i.city = 'Cupertino'
            i.phone = '0451 202 7' + str(a)
            i.address = '1 Infinite Loop'
            a += 1
            i.save()

        print 'Munging GSX account names'
        a = 65
        for i in GsxAccount.objects.all():
            i.title = 'GSX Account %s' % chr(a)
            a += 1
            i.save()

