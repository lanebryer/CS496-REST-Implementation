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
        new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'], at_sea=True, parent=parent_key)
        new_boat.put()
        new_boat.id = str(new_boat.key.urlsafe())
        new_boat.put()
        boat_dict = new_boat.to_dict()
        boat_dict['self'] = '/boat/' + new_boat.id
        self.response.write(json.dumps(boat_dict))

    def get(self, id=None):
        if id:
            boat = ndb.Key(urlsafe=id).get()
            if boat:
                boat_dict = boat.to_dict()
                boat_dict['self'] = "/boat/" + id
                self.response.write(json.dumps(boat_dict))
            else:
                self.response.status_int = 403
                self.response.write("Boat not found")
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
            boat = ndb.Key(urlsafe=id).get()
            if boat:
                boat.key.delete()
                self.response.status_int = 200
                self.response.write("Boat deleted")
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
        new_slip = Slip(number=slip_data['number'])
        new_slip.put()
        new_slip.id = str(new_slip.key.urlsafe())
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['self'] = '/slip/' + new_slip.id
        self.response.write(json.dumps(slip_dict))

    def get(self, id=None):
        if id:
            slip = ndb.Key(urlsafe=id).get()
            if slip:
                slip_dict = slip.to_dict()
                slip_dict['self'] = '/slip' + id
                self.response.write(json.dumps(slip_dict))
            else:
                self.response.status_int = 403
                self.response.write("Slip not found")
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
            slip = ndb.Key(urlsafe=id).get()
            if slip:
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
            slip = ndb.Key(urlsafe=id).get()
            if slip:
                patch_data = json.loads(self.request.body)
                for item in patch_data:
                    if item == "id" or item == "current_boat" or item == "arrival_date":
                        self.response.status_int = 403
                        self.response.write("ERROR: id and current_boat are read-only values")
                        break
                    if item == "number":
                        slip.number = patch_data['number']
                        slip.put()



class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write("Hi there")



allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler)
], debug=True)
