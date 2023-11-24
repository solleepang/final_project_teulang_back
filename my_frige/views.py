from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from teulang.settings import env
from my_frige.models import MyFrigeInside
from my_frige.serializers import MyFrigeInsideSerializer
from articles.models import ArticleRecipe


class MyFrigeView(APIView):
    """ 내 냉장고 내역 조회/등록/수정/삭제 """

    def get(self, request, user_id):
        """ user_id 유저의 냉장고 내역 조회 : 해당 유저만 볼 수 있도록 
            TODO?: 페이지네이션 필요함? 등록해봤자 20개 안 넘어 갈 것 같음 일단 구현 안함(프론트 전달)"""
        
        if not request.user.is_authenticated:
            return Response({"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.id != user_id:
            return Response({"message": "접근 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
            
        frige_inside = MyFrigeInside.objects.filter(user_id=user_id).order_by('expiration_date')
        serializer = MyFrigeInsideSerializer(frige_inside, many=True)
        warning_state_ingredients = [x.title for x in frige_inside.filter(state=2)]
        print(warning_state_ingredients)
        recipes = []
        for i in range(len(warning_state_ingredients)):
            if i < 1:
                recipes = ArticleRecipe.objects.filter(
                    recipe_ingredients__ingredients__contains=warning_state_ingredients[i].strip()
                ).distinct()
                print(recipes)
            else:
                recipes = recipes.filter(
                    recipe_ingredients__ingredients__contains=warning_state_ingredients[i].strip()
                ).distinct()
        print(recipes)
        if recipes:
            recommend_data = {
                "recommand_recipe_id": recipes[0].id,
                "warning_state_ingredients": warning_state_ingredients
            }
            return Response({"recommend_data":recommend_data, "frige_serializer_data":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, user_id):
        """ user_id 유저의 냉장고 내역 등록 """
        if not request.user.is_authenticated:
            return Response({"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_email_verified:
            return Response({"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN)
        if request.user.id != user_id:
            return Response({"message": "접근 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        data_set = eval(request.data.get('data_set'))
        serializer = MyFrigeInsideSerializer(data=data_set, many=True)

        if serializer.is_valid():
            serializer.save(user_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id, ingredient_id):
        """ user_id 유저의 특정 냉장고 내역 수정 """
        if not request.user.is_authenticated:
            return Response({"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.id != user_id:
            return Response({"message": "접근 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        frige_inside = get_object_or_404(MyFrigeInside, id=ingredient_id)
        if request.user == frige_inside.user_id:
            serializer = MyFrigeInsideSerializer(frige_inside, data=request.data)
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)  
    
    def delete(self, request, user_id, ingredient_id):
        """ user_id 유저의 특정 냉장고 내역 삭제 """
        if not request.user.is_authenticated:
            return Response({"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.id != user_id:
            return Response({"message": "접근 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        frige_inside = get_object_or_404(MyFrigeInside, id=ingredient_id)    
        if request.user == frige_inside.user_id:
            frige_inside.delete()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "삭제권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
