from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json
from views import get_authorized_user_ids
from sqlalchemy import and_
from views import can_view_post

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following
        authorized_users = get_authorized_user_ids(self.current_user)
        following = Following.query.filter(and_(Following.user_id==self.current_user.id, Following.user_id.in_(authorized_users))).all()
        data = [follow.to_dict_following() for follow in following] 

        return Response(json.dumps(data), mimetype="application/json", status=200)

    def post(self):
        # create a new "following" record based on the data posted in the body 
        body = request.get_json()
        try:
            following_id = int(body.get('user_id'))
        except:
            return Response(json.dumps({'message': 'User id must be int'}), mimetype="application/json",status=400)
        # if not body.get('user_id') or not can_view_post(body.get('post_id'), self.current_user):

        following = Following.query.filter_by(user_id = self.current_user.id).filter_by(following_id=following_id).all()
        if following:
            return Response(json.dumps({'message': 'already following user'}), mimetype="application/json", status=400)

        user_exist = User.query.get(following_id)
        if not user_exist:
            return Response(json.dumps({"message": "user does not exist"}), mimetype="application/json", status=404)

        follow = Following(user_id = self.current_user.id, following_id = following_id)

        db.session.add(follow)
        db.session.commit()
        return Response(json.dumps(follow.to_dict_following()), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        following = Following.query.get(id)
        if not following:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
            # return Response(json.dumps({"message":  "invalid id"}), mimetype="application/json", status=404)

        if following.user_id != self.current_user.id:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)


        Following.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message":  "Post id={0} successfully deleted".format(id)}), mimetype="application/json", status=200)
        return Response(json.dumps({}), mimetype="application/json", status=200)




def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
