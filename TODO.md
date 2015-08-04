- Move CSV generation to streamingoutput?

New checkin
===========

- Add buttons for lookups
- Highlight required fields
- Check that tabbing works OK in customer form
- Default checklist items to none, make mandatory
- Add warning icon if SN not valid Apple SN
- [OK] Add progress indication to new checkin
- [OK] Make password field mandatory
- [OK] Add warranty status to new checkin
- [OK] Password > Passcode for iPhones/iPads
- [OK] Make notify inline (hide for now)
- [OK] Default checkin/out location to current location
- [OK] Add condition text field, mandatory, append text to problem description.
- [OK] Move tags to top of problem description
- [OK] Hide terms checkbox from staff
- [OK] Show service order number on OK page
- [OK] For staff > go straight to printout
- [OK] Add accessories
- Add reseller (ask Apple/GSX)
- 
- Add "device description contains" to repair stats
- 

- Cleanup: customer dupes.


18.05.2015
==========
- Add SMS checkbox to customer?
- Check Mail-in repair creation API
- Add GSX repair confirmation variable to templates
- CLC PDF form autofill
- Add GSX repair "import" (by entering confirmation number)

- Should have a way to update part prices in the background
-- Add price_updated_at field

Admin:
- users&groups: active/inactive
- 

- Remove hidden users from stats
- Default checkin accessories to None and make it required (maybe select None or something (requred))

- Checkin should have login
-- Create case
-- See their history
-- See ongoing cases
-- Show everything you would show on paper
-- See status
-- Print dispatch form
-- Customer number instead of email
-- Generate URL for operator
-- Should also be able to create cases without logging

-- Add delivery methods without notifications
-- Klarna support for payments

-- Make welcome and title texts in checkin editable, on every page.


19.04.2014
- A way to manually update part  confirmations and return orders


13.04.2014
==========
- returns > add "Verify shipment" to check that selected parts are kosher (not returned, have ret numbers etc...)
- Checkin -> add delivery method + notifications for certain methods (courier, UPS,...)

29.11.13
========
- add "recent searches" to toolbar (check Twitter)
- Add stats per device type
- Put all accounts under servoapp.com
- Add country field to locations?
- Check consumer law support

- Add news feed feature


Random notes
============
ALTER SEQUENCE servo_order_id_seq RESTART WITH 12345

19.09.13
========
- Fix part DOA
- Improve note template caching


TODO:
=====
- Add command to download Servo/GSX repair in "GSX-format"
- Allow closing repairs that have been deleted from GSX
- Should somehow change request.session['gsx_account'] when setting new default GSX act?
- Can product A be dispatched from location B if it was ordered from location C?
- checkmail.py should support more than one API user...
- Check why Replacement parts are added as modules
- Slow GSX requests seem to lock up the app...
- [feature] Update part details from GSX (kinda like with devices)
- [feature] Add received_at to Device. Stamped when a device arrives at a given location.
- [bug] Cannot mix different payment methods
- [feature] Implement API (https://bitbucket.org/jespern/django-piston/wiki/Home, http://oauth.net)
- Update products list from MacTracker
- Store replacement devices as a device. Link to old device and customer. Once we know the SN of the replacement.
- Move all static files to web server
- Test restarting the server
- Add order codes to notifications list
- checkmail missed this one: https://servo.mcare.fi/notes/unread/2113/view/
- Printouts don't support folding very well
- Data detectors for notes and labels! (if email do this, if old system ID do that, if tracking ID do that...)
- Add link back to order to devices, products, custumers
- Some SN barcodes don't work
- Need some kind of manual
- Parts/receive - add text field for repair confirmations, show only matching results on submit
- [feature] Add Create Escalation to /notes
- [feature] Add device info into sidebar of orders/edit_product
- [bug] Repair total in gsx form sidebar is incorrect
- [bug] Add "More.." link to notification popup in navbar
- [feature] Keyboard shortcuts for main areas of system and search field focus
- [bug] Report invalid serial number searches in a nicer fashion:
File "/data/servo/lib/python2.7/site-packages/django/core/handlers/base.py", line 115, in get_response
    response = callback(request, *callback_args, **callback_kwargs)
  File "./servo/views/device.py", line 299, in search_gsx
    return get_gsx_search_results(request, what, param, query)
  File "./servo/views/device.py", line 219, in get_gsx_search_results
    result = Device.from_gsx(query)
  File "./servo/models/device.py", line 156, in from_gsx
    raise ValueError(_("Invalid serial number: %s" % sn))

- [feature] Show KGB SN in shipments/receive form
- [feature] Append text from template chooser instead of replacing
- [bug] Don't sync POI and SOI SN:s when receiving
- [feature] Creating product that already exists should edit exising product and add new device as product category
- [feature] Upload DB backups
- [feature] shelf codes!
- [feature] Gsx Session manager (check which session ID belongs to what account, add queueing)
- Printing receipts and dispatches
- [feature] Add delivery method to orders
- [bug] Customers with full-caps names with non-ascii chars can only be found wih full caps
- [bug] Cannot remove more than one accessory
- [bug] Cannot create new device from device chooser
- a smarter price calculator
- Add queue to all users when creating queue
- Add Print label button to view bulk return page
- uppercase all serial numbers (including KBB and KGB)
- Show closed GSX repairs as disabled in Order/edit
- [feature] Show average age in every order listing?
- [bug] Cannot handle validation errors in modals?
- How to handle GSX timeouts?
- Should not be able to change part which has been ordered
- Add initiate iOS diagnostics
- Add MRI results for Macs
[bug] WARNING:py.warnings:/data/servo/lib/python2.7/site-packages/django/db/models/fields/__init__.py:782: RuntimeWarning: DateTimeField received a naive datetime (2013-03-18 00:00:00) while time zone support is active.
  RuntimeWarning)

- [feature] Parts library (with checkin/checkout)
- [bug] Cannot browse received parts by date
- [feature] Make layout more responsive (hide search field)
- [bug] Status time deltas should only consider working days.
- [feature] Strip leading S-characters from serial numbers

- adding parts to GSX repairs
- Saveable searches!
- setup wizard
- global login which redirects to the specific app
- logging in as a customer (limiting search results, customers, orders, permissions, etc)

- Create generic print templates for repair confirmation(done) and receipt
- products/outgoing
- products/incoming
- products/invoices
- modals for GSX submits (so that users don't interrupt the long requests)
- test permissions

- [gsxbug] Using non-serialized SN doesn't seem to work ("A repair is already open for this unit. GSX does not allow more than one repair to be open for each unit.")
- [enhancement] Move to using reverse() in get_absolute_url's

For the next version
====================
- [feature] Add Finnish ZIP code lookup
- shared calendars
- Password resets
- an actually useful troubleshooting tool

