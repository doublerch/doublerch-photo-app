from flask import Response, request
from flask_restful import Resource
from models import LikePost, db
import json
from views import can_view_post

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "like_post" based on the data posted in the body 
        body = request.get_json()
        try:
            pid = int(body.get('post_id'))
        except:
            return Response(json.dumps({'message': 'Post id must be int'}), mimetype="application/json",status=400)        
        
        if not body.get('post_id') or not can_view_post(body.get('post_id'), self.current_user):
            return Response(json.dumps({'message': 'post not found'}), mimetype="application/json", status=404)
        
        liked_posts = LikePost.query.filter(LikePost.user_id == self.current_user.id)
        for liked_post in liked_posts:
            if liked_post.post_id == body.get('post_id'):
                return Response(json.dumps({'message': 'post already liked'}), mimetype="application/json", status=400)

        like = LikePost(
            user_id = self.current_user.id,
            post_id = body.get('post_id')
        )

        db.session.add(like)
        db.session.commit()
        return Response(json.dumps(like.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "like_post" where "id"=id
        liked_post = LikePost.query.get(id)
        if not liked_post:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)

        if liked_post.user_id != self.current_user.id:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)


        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message":  "LikedPost id={0} successfully deleted".format(id)}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/likes', 
        '/api/posts/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/likes/<int:id>', 
        '/api/posts/likes/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
