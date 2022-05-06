from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from views import can_view_post, get_authorized_user_ids

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "Comment" based on the data posted in the body 
        body = request.get_json()
        # print(body)
        try:
            pid = int(body.get('post_id'))
        except:
            return Response(json.dumps({'message': 'Post id must be int'}), mimetype="application/json",status=400)

        if not body.get('text'):
            return Response(json.dumps({'message': 'invalid comment'}), mimetype="application/json", status=400)
        
        authorized_users = get_authorized_user_ids(self.current_user)
        # print ("post_id")
        # print (body.get('post_id'))
        # print ("user_id")
        # print (body.get("user_id"))
        # print ("authorized users")
        # print(authorized_users)

        if not body.get('post_id') or not can_view_post(body.get('post_id'), self.current_user):
            return Response(json.dumps({'message': 'post not found'}), mimetype="application/json", status=404)
        comment = Comment(
            text = body.get('text'), 
            user_id = self.current_user.id,
            post_id = body.get('post_id')
        )

        db.session.add(comment)
        db.session.commit()
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    def delete(self, id):
        # delete "Comment" record where "id"=id
        comment = Comment.query.get(id)
        if not comment:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
            # return Response(json.dumps({"message":  "invalid id"}), mimetype="application/json", status=404)

        if comment.user_id != self.current_user.id:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)


        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message":  "Post id={0} successfully deleted".format(id)}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
