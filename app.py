from google.appengine.ext import ndb
import webapp2
import json

class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)
    at_sea = ndb.BooleanProperty()

class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        parent_key = ndb.Key(Boat, "parent_boat")
        boat_data = json.loads(self.request.body)
        nameExists = False
        typeExists = False
        lengthExists = False
        for i in boat_data:
            if i == "name":
                nameExists = True
            elif i == "type":
                typeExists = True
            elif i == "length":
                lengthExists = True

        if nameExists == False or typeExists == False or lengthExists == False:
            self.response.status_int = 403;
            self.response.write("ERROR 403: You must specify name, type, and length fields")
        else:
            new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'], at_sea=True, parent=parent_key)
            new_boat.put()
            new_boat.id = str(new_boat.key.urlsafe())
            new_boat.put()
            boat_dict = new_boat.to_dict()
            boat_dict['self'] = '/boat/' + new_boat.id
            self.response.write(json.dumps(boat_dict))

    def get(self, id=None):
        if id:
            boatFound = False
            boats = Boat.query()
            for boat in boats:
                if boat.id == id:
                    boatFound = True
            if boatFound == True:
                foundBoat = ndb.Key(urlsafe=id).get()
                boat_dict = foundBoat.to_dict()
                boat_dict['self'] = "/boat/" + id
                self.response.write(json.dumps(boat_dict))
            else:
                self.response.status_int = 403
                self.response.write("ERROR 403: ID not found")
        else:
            boats = Boat.query().fetch()
            boat_dicts = {"Results": []}
            for boat in boats:
                boat_data = boat.to_dict()
                boat_data['self'] = '/boat/' + boat.key.urlsafe()
                boat_dicts['Results'].append(boat_data)
            self.response.write(json.dumps(boat_dicts))

    def delete(self, id=None):
        if id:
            boatFound = False
            boats = Boat.query()
            for boat in boats:
                if boat.id == id:
                    boatFound = True
            if boatFound == True:
                foundBoat = ndb.Key(urlsafe=id).get()
                slips = Slip.query()
                slipId = ""
                slipFound = False

                for slip in slips:
                    if slip.current_boat:
                        if slip.current_boat == id:
                            slip.current_boat = None
                            slip.arrival_date = None
                            slip.put()

                foundBoat.key.delete()
                self.response.status_int = 200
                self.response.write("Boat deleted")
            else:
                self.response.status_int = 403
                self.response.write("ERROR 403: ID not found")
        else:
            self.response.status_int = 403
            self.response.status_message = "ID not provided"
            self.response.write("ERROR: ID not provided")

    def patch(self, id=None):
        if id:
            boatFound = False
            boats = Boat.query()
            for boat in boats:
                if boat.id == id:
                    boatFound = True

            if boatFound == True:
                boat = ndb.Key(urlsafe=id).get()
                patch_data = json.loads(self.request.body)
                edited = False
                invalidValue = False
                for item in patch_data:
                    if item == "id" or item == "at_sea":
                        invalidValue = True
                    elif item == "name":
                        boat.name = patch_data['name']
                        edited=True
                    elif item == "length":
                        boat.length = patch_data['length']
                        edited=True
                    elif item == "type":
                        boat.type = patch_data['type']
                        edited=True

                if invalidValue == True:
                    self.response.status_int = 403
                    self.response.write("ERROR 403: id and at_sea are read-only values\n")

                if edited == True:
                    boat.put()
                    boat_dict = boat.to_dict()
                    boat_dict['self'] = '/boat/' + boat.key.urlsafe()
                    self.response.write(json.dumps(boat_dict))

            else:
                self.response.status_int = 403
                self.response.status_message = "ID not found"
                self.response.write("ERROR: ID not found")
        else:
            self.response.status_int = 403
            self.response.status_message = "ID not provided"
            self.response.write("ERROR: ID not provided")



class SlipHandler(webapp2.RequestHandler):
    def post(self):
        parent_key = ndb.Key(Slip, "parent_slip")
        slip_data = json.loads(self.request.body)
        slips = Slip.query()
        numberExists = False
        numberFound = False

        if 'number' in slip_data:
            numberFound = True

        if numberFound == True:
            if slips:
                for i in slips:
                    if i.number == slip_data['number']:
                        numberExists = True

                    if numberExists == True:
                        self.response.status_int = 403
                        self.response.write("ERROR 403: Slip with that number already exists")
                        break
                else:
                    new_slip = Slip(number=slip_data['number'], current_boat = None, parent=parent_key)
                    new_slip.put()
                    new_slip.id = str(new_slip.key.urlsafe())
                    new_slip.put()
                    slip_dict = new_slip.to_dict()
                    slip_dict['self'] = '/slip/' + new_slip.id
                    self.response.write(json.dumps(slip_dict))
        else:
            self.response.status_int = 403
            self.response.write("ERROR 403: number field not specified")

    def get(self, id=None):
        if id:
            slipFound = False
            slips = Slip.query()
            for slip in slips:
                if slip.id == id:
                    slipFound = True
            if slipFound == True:
                foundSlip = ndb.Key(urlsafe=id).get()
                slip_dict = foundSlip.to_dict()
                slip_dict['self'] = "/slip/" + id
                self.response.write(json.dumps(slip_dict))
            else:
                self.response.status_int = 403
                self.response.write("ERROR 403: ID not found")
        else:
            slips = Slip.query().fetch()
            slip_dicts = {"Results": []}
            for slip in slips:
                slip_data = slip.to_dict()
                slip_data['self'] = '/slip/' + slip.key.urlsafe()
                slip_dicts['Results'].append(slip_data)
            self.response.write(json.dumps(slip_dicts))

    def delete(self, id=None):
        if id:
            slipFound = False
            slips = Slip.query()
            for slip in slips:
                if slip.id == id:
                    slipFound = True
            if slipFound == True:
                slip = ndb.Key(urlsafe=id).get()
                if slip.current_boat:
                    boats = Boat.query()
                    for boat in boats:
                        if boat.id == slip.current_boat:
                            boat.at_sea = True
                            boat.put()
                slip.key.delete()
                self.response.status_int = 200
                self.response.write("Slip deleted")
            else:
                self.response.status_int = 403
                self.response.status_message = "ID not found"
                self.response.write("ERROR: ID not found")
        else:
            self.response.status_int = 403
            self.response.status_message = "ID not provided"
            self.response.write("ERROR: ID not provided")

    def patch(self, id=None):
        if id:
            slipFound = False
            slips = Slip.query()
            for slip in slips:
                if slip.id == id:
                    slipFound = True

            if slipFound == True:
                slip = ndb.Key(urlsafe=id).get()
                if slip:
                    patch_data = json.loads(self.request.body)
                    for item in patch_data:
                        if item == "id" or item == "current_boat" or item == "arrival_date":
                            self.response.status_int = 403
                            self.response.write("ERROR: id, current_boat, and arrival_date are read-only values")
                            break
                        if item == "number":
                            slipFound = False
                            slips = Slip.query().fetch()
                            for i in slips:
                                if i.number == patch_data['number']:
                                    slipFound = True

                            if slipFound == True:
                                self.response.status_int = 403
                                self.response.write("ERROR: Slip with that number already exists")
                            else:
                                slip.number = patch_data['number']
                                slip.put()
                                slip_dict = slip.to_dict()
                                slip_dict['self'] = '/slip/' + slip.key.urlsafe()
                                self.response.write(json.dumps(slip_dict))
            else:
                self.response.status_int = 403
                self.response.write("ERROR 403: ID not found")

class BoatInSlipHandler(webapp2.RequestHandler):
    def get(self, id=None):
        if id:
            slipFound = False
            slips = Slip.query()
            for slip in slips:
                if slip.id == id:
                    slipFound = True
            if slipFound == True:
                slip = ndb.Key(urlsafe=id).get()
                if slip.current_boat == None:
                    self.response.status_int = 403
                    self.response.write("ERROR 403: There is no boat in the slip")
                else:
                    boat = ndb.Key(urlsafe=slip.current_boat).get()
                    boat_dict = boat.to_dict()
                    boat_dict['self'] = "/boat/" + boat.id
                    self.response.write(json.dumps(boat_dict))
            else:
                self.response.status_int = 403
                self.response.write("ID not found")
        else:
            self.response.status_int = 403
            self.response.write("ID not provided")

    def put(self, id=None):
        if id:
            slipFound = False
            slips = Slip.query()
            for slip in slips:
                if slip.id == id:
                    slipFound = True
            if slipFound == True:
                slip = ndb.Key(urlsafe=id).get()
                put_data = json.loads(self.request.body)
                boatFound = False
                arrivalDateFound = False
                for item in put_data:
                    if item == "id":
                        boatFound = True
                    if item == "arrival_date":
                        arrivalDateFound = True

                if boatFound == False or arrivalDateFound == False:
                    self.response.status_int = 403
                    self.response.write("ERROR: body data requires 'id' and 'arrival_date'")
                    return

                boatId = put_data['id']
                boats = Boat.query()
                boatIdFound = False
                for boat in boats:
                    if boat.id == boatId:
                        boatIdFound = True

                if boatIdFound == False:
                    self.response.status_int = 403
                    self.response.write("ERROR: Boat not found")
                    return

                elif slip.current_boat != None:
                    self.response.status_int = 403
                    self.response.write("ERROR: slip is already occupied")

                else:
                    boat = ndb.Key(urlsafe=boatId).get()
                    if boat.at_sea == False:
                        self.response.status_int = 403
                        self.response.write("ERROR: Boat is already in a slip")
                    else:
                        boat.at_sea = True
                        boat.put()
                        slip.current_boat = put_data['id']
                        slip.arrival_date = put_data['arrival_date']
                        boat.at_sea = False
                        slip.put()
                        boat.put()
                        slip_dict = slip.to_dict()
                        slip_dict['self'] = "/slip/" + slip.id
                        self.response.write(json.dumps(slip_dict))
            else:
                self.response.status_int = 403
                self.response.write("ERROR: Slip not found")
        else:
            self.response.status_int = 403
            self.response.write("ERROR: ID not provided")


class BoatAtSeaHandler(webapp2.RequestHandler):
    def put(self, id=None):
        if id:
            boatFound = False
            boats = Boat.query()
            for boat in boats:
                if boat.id == id:
                    boatFound = True
            if boatFound == True:
                boat = ndb.Key(urlsafe=id).get()

                if boat.at_sea == True:
                    self.response.status_int = 403
                    self.response.write("Boat is already at sea")
                else:
                    slips = Slip.query()
                    for slip in slips:
                        if slip.current_boat == id:
                            slip.current_boat = None
                            slip.arrival_date = None
                            slip.put()
                    boat.at_sea = True
                    boat.put()
                    boat_dict = boat.to_dict()
                    boat_dict['self'] = "/boat/" + id
                    self.response.write(json.dumps(boat_dict))
            else:
                self.response.status_int = 403
                self.response.write("ERROR 403: ID not found")
        else:
            self.response.status_int = 403
            self.response.write("ERROR 403: ID not provided")


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write("Hi there")


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boat', BoatHandler),
    ('/boat/([A-z0-9\-]+)', BoatHandler),
    ('/boat/([A-z0-9\-]+)/at_sea', BoatAtSeaHandler),
    ('/slip', SlipHandler),
    ('/slip/([A-z0-9\-]+)', SlipHandler),
    ('/slip/([A-z0-9\-]+)/boat', BoatInSlipHandler)
], debug=True)
