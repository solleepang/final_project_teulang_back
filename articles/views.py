from django.shortcuts import render
from rest_framework.views import APIView

class CommentView(APIView):
    
    def get(self,request):
        """ 특정 recipe의 댓글 조회 """
        pass
    
    def post(self,request,recipe_id):
        """ 댓글 작성 """
        pass
    
    def put(self,request,recipe_id):
        """ 댓글 수정 """
        pass

    def delete(self,request,recipe_id):
        """ 댓글 삭제 """
        pass

