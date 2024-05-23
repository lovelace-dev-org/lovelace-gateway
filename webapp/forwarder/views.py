from functools import wraps
from urllib.parse import urljoin
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from forwarder.forms import ForwardForm, RegisterForm
import forwarder.models as fm

# Create your views here.

def cookie_law(view_func):
    """
    To comply with the European Union cookie law, display a warning about the
    site using cookies. When the user accepts cookies, set a session variable to
    disable the message.
    """

    @wraps(view_func)
    def func_wrapper(obj, request, *args, **kwargs):
        if "cookies_accepted" in request.COOKIES:
            if request.COOKIES["cookies_accepted"] == "1":
                request.session["cookies_accepted"] = True
        if request.session.get("cookies_accepted"):
            pass
        else:
            request.session["cookies_accepted"] = False
        return view_func(obj, request, *args, **kwargs)

    return func_wrapper


class Index(View):

    @cookie_law
    def get(self, request):
        if "forward_target" in request.COOKIES:
            return redirect(request.COOKIES["forward_target"])

        form = ForwardForm()
        return render(
            request,
            "forwarder/form.html",
            {
                "submit_url": request.path,
                "form_object": form,
                "disclaimer": _("Fill your student ID into this form")
            }
        )

    def post(self, request):
        form = ForwardForm(request.POST)
        if not form.is_valid():
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)

        record = form.cleaned_data["record"]
        if not record.created:
            return JsonResponse({
                "redirect": reverse(
                    "register", kwargs={"student_id": form.cleaned_data["student_id"]}
                )
            })

        response = JsonResponse(
            {"redirect": record.target_host}
        )
        response.set_cookie(
            "forward_target",
            value=record.target_host
        )
        return response


class Register(View):

    @cookie_law
    def get(self, request, student_id):
        if "forward_target" in request.COOKIES:
            return redirect(request.COOKIES["forward_target"])

        form = RegisterForm(initial={"student_id": student_id})
        return render(
            request,
            "forwarder/form.html",
            {
                "submit_url": request.path,
                "form_object": form,
                "disclaimer": _("Enter a password for your account")
            }
        )

    def post(self, request, student_id):
        form = RegisterForm(request.POST)
        if not form.is_valid():
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)

        record = form.cleaned_data["record"]
        api_response = requests.post(
            urljoin(record.target_host, "api/users/"),
            json={
                "username": record.student_id,
                "password": form.cleaned_data["password"],
                "first_name": record.first_name,
                "last_name": record.last_name,
                "email": record.email,
                "student_id": record.student_id,
            },
            headers={
                "x-lovelace-api-key": settings.LOVELACE_MANAGEMENT_API_KEY
            }
        )
        if api_response.status_code != 201:
            # notify admin
            return JsonResponse(status=400)

        record.created = True
        record.save()

        response = JsonResponse(
            {"redirect": record.target_host}
        )
        response.set_cookie(
            "forward_target",
            value=record.target_host
        )
        return response
