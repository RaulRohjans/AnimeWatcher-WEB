import django.views.defaults
from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .forms import ChangePasswordForm, ChangeAccountSettingsForm
from .utils import token_generator, hasNumbers

from rest_framework.authtoken.models import Token

import threading


# Methods
class EmailThread(threading.Thread):

    # Constructor
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect('home')
            else:
                messages.error(request, 'Your username or password is incorrect.', extra_tags='error')

        return render(request, "authentication/login.html", {})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            termsConditions = request.POST.get('terms')
            form_username = request.POST.get('username')
            form_email = request.POST.get('email')
            form_pass1 = request.POST.get('password1')
            form_pass2 = request.POST.get('password2')

            if form_username and form_email and form_pass1 and form_pass2:
                if form_pass2 == form_pass1:
                    contains_letters = form_pass1.lower()
                    if len(form_pass1) >= 8 and hasNumbers(form_pass1) and contains_letters.islower():
                        # Check if the email and username are already in use
                        userObjs = User.objects.all()
                        EmailInUse = False
                        UserInUse = False

                        for obj in userObjs:
                            if obj.email == form_email:
                                EmailInUse = True
                            if obj.username == form_username:
                                UserInUse = True

                        if not EmailInUse:
                            if not UserInUse:
                                if termsConditions:
                                    user = User.objects.create_user(form_username, form_email, form_pass1)
                                    user.is_active = False  # This is because the user has to confirm their email
                                    user.save()

                                    # Send a confirmation email to the user
                                    domain = get_current_site(request).domain
                                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                                    link = reverse('account-activation',
                                                   kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                                    activate_url = request.scheme + '://' + domain + link

                                    email_subject = 'Please activate your account!'
                                    message = render_to_string('authentication/email-activate-account.html',
                                                               {
                                                                   'user': user,
                                                                   'protocol': request.scheme + '://',
                                                                   'domain': get_current_site(request).domain,
                                                                   'uid': urlsafe_base64_encode(
                                                                       force_bytes(user.pk)),
                                                                   'token': token_generator.make_token(user)
                                                               })
                                    email = EmailMessage(
                                        email_subject,
                                        message,
                                        settings.EMAIL_HOST_USER,
                                        [form_email]
                                    )
                                    email.content_subtype = 'html'
                                    EmailThread(email).start()
                                    messages.success(request, 'Account created successfully!')
                                    messages.success(request, 'Please check your email address to activate it.')

                                else:
                                    messages.error(request, 'You must agree to the terms and conditions!',
                                                   extra_tags='error')
                            else:
                                messages.error(request, 'That username is already in use!', extra_tags='error')
                        else:
                            messages.error(request, 'That email is already in use!', extra_tags='error')
                    else:
                        messages.error(request,
                                       'Your password must be more than 8 characters long and contain letters and at least one number!',
                                       extra_tags='error')
                else:
                    messages.error(request, 'Passwords don\'t match!!', extra_tags='error')
            else:
                messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

        context = {}

        return render(request, "authentication/register.html", context)


def verification_view(request, uidb64, token):
    try:
        id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=id)

        # Check if the token hasnt been used before
        if not token_generator.check_token(user, token):
            messages.error(request, 'Your account activation token is no longer valid!', extra_tags='error')
            return redirect('login')

        if user.is_active:
            return redirect('login')
        user.is_active = True
        user.save()

        main_url = request.scheme + '://' + get_current_site(request).domain
        return render(request, "authentication/account-activated-success.html", {'main_url': main_url})
    except DjangoUnicodeDecodeError as ee:
        messages.error(request, 'Something went wrong setting your new password.', extra_tags='error')


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            form_email = request.POST.get('email')
            if form_email:

                # Check if there is a user with that email
                user = User.objects.filter(email=form_email)

                if user.exists():
                    email_subject = 'Reset your Password'
                    message = render_to_string('authentication/email-forgot-password.html',
                                               {
                                                   'protocol': request.scheme + '://',
                                                   'domain': get_current_site(request).domain,
                                                   'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                                   'token': PasswordResetTokenGenerator().make_token(user[0])
                                               })
                    message_text = strip_tags(message)
                    email = EmailMessage(
                        email_subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [form_email],
                    )
                    email.content_subtype = 'html'
                    EmailThread(email).start()

                messages.success(request, 'We have sent you an email with instructions on how to reset your password!')
            else:
                messages.error(request, 'Please insert an email address!', extra_tags='error')

        context = {}
        return render(request, "authentication/forgot-password.html", context)


def recover_password_view(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'Password reset link is invalid, please request another one.',
                               extra_tags='error')
                return redirect('forgot-password')

            if request.method == 'POST':
                form_pass1 = request.POST.get('password1')
                form_pass2 = request.POST.get('password2')

                if form_pass1 and form_pass2:
                    if form_pass2 == form_pass1:
                        contains_letters = form_pass1.lower()
                        if len(form_pass1) >= 8 and hasNumbers(form_pass1) and contains_letters.islower():

                            user.set_password(form_pass1)
                            user.save()

                            # Get website main URL
                            main_url = request.scheme + '://' + get_current_site(request).domain
                            return render(request, "authentication/password-reset-success.html", {'main_url': main_url})
                        else:
                            messages.error(request,
                                           'Your password must be more than 8 characters long and contain letters and at least one number!',
                                           extra_tags='error')
                    else:
                        messages.error(request, 'Passwords don\'t match!', extra_tags='error')
                else:
                    messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

            context = {}
            return render(request, "authentication/recover-password.html", context)
        except DjangoUnicodeDecodeError as i:
            messages.error(request, 'Something went wrong setting your new password.', extra_tags='error')


@login_required(login_url='login')
def change_password_view(request):
    form = ChangePasswordForm(None)

    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated successfully!')

    context = {
        'form': form,
        'username': request.user.username,
    }
    return render(request, "authentication/change-password.html", context)


def change_password_token_view(request, token):
    form = ChangePasswordForm(None)
    print(token)
    try:
        tokenObj = Token.objects.get(key=token)
        if tokenObj is not None:
            user = User.objects.get(pk=tokenObj.user_id)
            if user is not None and user.is_active:
                if request.method == 'POST':
                    form = ChangePasswordForm(user, request.POST)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Password updated successfully!')

                context = {
                    'form': form,
                    'username': user.username,
                }
                return render(request, "authentication/change-password.html", context)
            else:
                django.views.defaults.page_not_found()
        else:
            django.views.defaults.page_not_found()
    except Token.DoesNotExist:
        django.views.defaults.page_not_found()


@login_required(login_url='login')
def account_settings_view(request):
    if request.method == 'POST':
        form = ChangeAccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings applied successfully!')
    else:
        form = ChangeAccountSettingsForm(instance=request.user)

    context = {
        'form': form,
        'username_value': request.user.username,
        'email_value': request.user.email,
    }
    return render(request, "authentication/account-settings.html", context)


def account_settings_token_view(request, token):
    try:
        tokenObj = Token.objects.get(key=token)
        if tokenObj is not None:
            user = User.objects.get(pk=tokenObj.user_id)
            if user is not None:
                form = ChangeAccountSettingsForm(instance=user)

                if request.method == 'POST':
                    form = ChangeAccountSettingsForm(request.POST, instance=user)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Settings applied successfully!')

                context = {
                    'form': form,
                    'username_value': user.username,
                    'email_value': user.email,
                }
                return render(request, "authentication/account-settings.html", context)
            else:
                django.views.defaults.page_not_found()

        else:
            django.views.defaults.page_not_found()
    except Token.DoesNotExist:
        django.views.defaults.page_not_found()
