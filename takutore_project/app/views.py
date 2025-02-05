from django.shortcuts import render, redirect  # HTMLテンプレートのレンダリングとリダイレクト用
from django.views import View  # クラスベースビューを利用するためのインポート
from django.contrib.auth import login, update_session_auth_hash  # ユーザーをログイン状態にするための関数
from django.contrib.auth.mixins import LoginRequiredMixin  # ログインが必要なビューを作成するためのミックスイン
from django.contrib.auth.models import User # DBモデルをインポート
from app.forms import SignupForm, LoginForm, MypageForm, PasswordChangeForm  # 作成したフォームをインポート

# Create your views here.

# ポートフォリオページを表示するビュー（ログイン不要）
class PortfolioView(View):
    def get(self, request): # GETリクエストが送られたときの処理
        return render(request, "portfolio.html")  # portfolio.htmlを表示

# ユーザー新規登録を行うビュー
class SignupView(View):
    def get(self, request):  # GETリクエストが送られたとき（新規登録フォームを表示）
        form = SignupForm()  # 空のサインアップフォームを作成
        return render(request, "signup.html", context={
            "form":form  # テンプレートにフォームを渡す
        })
    def post(self, request):  # POSTリクエストが送られたとき（フォームが送信されたとき）
        print(request.POST)   # デバッグ用にフォームのデータを表示（不要なら削除可）
        form = SignupForm(request.POST)   #ユーザーが入力したデータを取得
        if form.is_valid():   # ユーザーが入力したデータが正しい形式かチェック
            user = form.save()  # 入力されたデータをUserデータベースに保存
            login(request, user)  # 保存したユーザーをログイン状態にする
            return redirect("home")  # # 保存後にホームへリダイレクト
        return render(request, "signup.html", context={
            "form":form  # 入力にエラーがある場合、フォームとエラーを再表示
        })

# ユーザーログインを処理するビュー
class LoginView(View):
    def get(self, request):  # GETリクエストが送られたとき（ログインページを表示）
        return render(request, "login.html")
    
    def post(self, request): # POSTリクエストが送られたとき（ログインフォームが送信されたとき）
        print(request.POST)
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("home")
        return render(request, "login.html", context={
            "form":form
        })

# トップページビュー（ログインが必要）
class HomeView(LoginRequiredMixin, View):
    login_url = "login"  # ログインしていない場合、ログインページにリダイレクト
    def get(self, request):
        return render(request, "home.html")



# マイページビュー（ログインが必要）
class MypageView(LoginRequiredMixin, View):
    login_url = "login"
    def get(self, request):
        user = request.user  # 現在ログインしているユーザー情報を取得

         # ユーザー情報を変数に保存
        user_data = {
            "username": user.username,
            "email": user.email,
            "height": user.height,
            "weight": user.weight,
        }

        # テンプレートにデータを渡して表示
        return render(request, "mypage.html", context={
            "user_data": user_data
        })


# マイページ変更ビュー（ログインが必要）
class MyPageEditView(LoginRequiredMixin, View):
    login_url = "login"
    def get(self, request):
        user = request.user  # ログインしているユーザーを取得
        form = MypageForm(instance=user)  # ユーザーインスタンスを渡す

        return render(request, 'mypage_edit.html', {'form': form})

    def post(self, request):
        form = MypageForm(request.POST, instance=request.user)  # フォームにユーザーインスタンスを渡して保存
        if form.is_valid():
            form.save()  # データを保存
            return redirect('mypage')  # マイページへ移動
        return render(request, 'mypage_edit.html', {'form': form})


#パスワードの変更ビュー（ログインが必要）
class PasswordChangeView(LoginRequiredMixin, View):
    login_url = "login"
    def get(self, request):
        form = PasswordChangeForm(user=request.user)  # パスワード変更フォームを取得
        return render(request, 'password_change.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()  # パスワードを更新
            update_session_auth_hash(request, form.user)  # セッションの認証情報を更新（再ログイン防止）
            return redirect('mypage')  # パスワード変更成功後、マイページにリダイレクト
        return render(request, 'password_change.html', {'form': form})