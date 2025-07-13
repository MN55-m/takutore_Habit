from django.shortcuts import render, redirect  # HTMLテンプレートのレンダリングとリダイレクト用
from django.views import View  # クラスベースビューを利用するためのインポート
from django.contrib.auth import login, update_session_auth_hash  # ユーザーをログイン状態にするための関数
from django.contrib.auth.mixins import LoginRequiredMixin  # ログインが必要なビューを作成するためのミックスイン
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.shortcuts import redirect
from app.forms import SignupForm, LoginForm, MypageForm, PasswordChangeForm  # 作成したフォームをインポート
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import View
from app_workout.models import WorkoutRecord
from django.utils.timezone import localtime

User = get_user_model()  # カスタムユーザーモデルを取得

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
        user = request.user
        today = localtime().date()

        # 本日までの体重記録のうち、最新の1件（created_atの降順）
        latest_record = (
            WorkoutRecord.objects
            .filter(user=user, created_at__date__lte=today)
            .exclude(weight_record__isnull=True)
            .order_by('-created_at')
            .first()
        )

        # レコードがあればその体重、なければ初期体重
        current_weight = latest_record.weight_record if latest_record else user.weight

        # 身長から適正体重・美容体重を計算
        height = user.height
        height_m = height / 100
        appropriate_weight = round(22 * height_m * height_m, 1)
        beauty_weight = round(20 * height_m * height_m, 1)

        appropriate_diff = round(current_weight - appropriate_weight, 1) if current_weight else None
        beauty_diff = round(current_weight - beauty_weight, 1) if current_weight else None

        # 曜日も渡したいなら以下を追加
        weekday_japanese = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekday_japanese[today.weekday()]

        context = {
            'today': today,
            'weekday': weekday,
            'current_weight': current_weight,
            'ideal_weight': appropriate_weight,  # ← テンプレートに合わせて修正
            'beauty_weight': beauty_weight,
            'ideal_diff': abs(appropriate_diff) if appropriate_diff and appropriate_diff > 0 else 0,
            'beauty_diff': abs(beauty_diff) if beauty_diff and beauty_diff > 0 else 0,
        }

        return render(request, "home.html", context)


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
class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    login_url = "login"
    form_class = PasswordChangeForm  # 使用するフォームを指定
    template_name = 'password_change.html'  # パスワードの変更画面
    success_url = reverse_lazy('mypage')    # # パスワード変更成功後にリダイレクトするURL（マイページ）

    # フォームが正常に送信され、バリデーションが通った場合(form_valid)
    def form_valid(self, form):
        # ユーザー情報を保存してパスワードを変更
        user = form.save()  
        # セッションの認証情報を更新（新しいパスワードをセッションに反映させる）
        update_session_auth_hash(self.request, user)
        # 成功メッセージを追加
        messages.success(self.request, "パスワードが正常に変更されました。")
        # 成功後、マイページにリダイレクト
        return redirect(self.success_url)
    
    # フォームが無効な場合（エラーが発生した場合）(form_invalid)
    def form_invalid(self, form):
        # エラーがあった場合は、同じページに戻り、エラーメッセージを表示
        messages.error(self.request, "パスワードの変更に失敗しました。入力内容を確認してください。")
        return super().form_invalid(form)