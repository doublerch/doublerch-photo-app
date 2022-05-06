from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json
from views import can_view_post

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # get all bookmarks owned by the current user
        bookmarks = Bookmark.query.filter(Bookmark.user_id == self.current_user.id)
        data = [bookmark.to_dict() for bookmark in bookmarks]
        return Response(json.dumps(data), mimetype="application/json", status=200)

    def post(self):
        # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()
        # print(body)
        try:
            pid = int(body.get('post_id'))
        except:
            return Response(json.dumps({'message': 'Post id must be int'}), mimetype="application/json",status=400)

        if not body.get('post_id') or not can_view_post(body.get('post_id'), self.current_user):
            return Response(json.dumps({'message': 'post not found'}), mimetype="application/json", status=404)

        bookmarks = Bookmark.query.filter(Bookmark.user_id == self.current_user.id)
        for bookmark in bookmarks:
            if bookmark.post.id == body.get('post_id'):
                return Response(json.dumps({'message': 'post already bookmarked'}), mimetype="application/json", status=400)


        bookmark = Bookmark(
            post_id = body.get('post_id'), 
            user_id = self.current_user.id
        )
        db.session.add(bookmark)
        db.session.commit()
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "bookmark" record where "id"=id
        # print(id)
        bookmark = Bookmark.query.get(id)
        if not bookmark:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
            # return Response(json.dumps({"message":  "invalid id"}), mimetype="application/json", status=404)

        if bookmark.user_id != self.current_user.id:
            return Response(json.dumps({"message":  "id={0} is invalid".format(id)}), mimetype="application/json", status=404)


        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message":  "Bookmark id={0} successfully deleted".format(id)}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<int:id>', 
        '/api/bookmarks/<int:id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
