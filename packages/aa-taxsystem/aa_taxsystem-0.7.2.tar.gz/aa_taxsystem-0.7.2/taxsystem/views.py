"""PvE Views"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA TaxSystem
from taxsystem import __title__, forms, tasks
from taxsystem.api.helpers import (
    get_character_permissions,
    get_corporation,
    get_manage_corporation,
    get_manage_permission,
)
from taxsystem.helpers.views import add_info_to_context
from taxsystem.models.filters import JournalFilter, JournalFilterSet
from taxsystem.models.logs import AdminLogs, PaymentHistory
from taxsystem.models.tax import Members, OwnerAudit, Payments, PaymentSystem

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("taxsystem.basic_access")
def index(request: WSGIRequest):
    """Index View"""
    return redirect(
        "taxsystem:payments", request.user.profile.main_character.corporation_id
    )


@login_required
@permission_required("taxsystem.basic_access")
def admin(request: WSGIRequest):
    corporation_id = request.user.profile.main_character.corporation_id
    if not request.user.is_superuser:
        messages.error(request, _("You do not have permission to access this page."))
        return redirect("taxsystem:index")

    if request.method == "POST":
        force_refresh = False
        if request.POST.get("force_refresh", False):
            force_refresh = True
        if request.POST.get("run_clear_etag"):
            messages.info(request, _("Queued Clear All ETags"))
            tasks.clear_all_etags.apply_async(priority=1)
        if request.POST.get("run_taxsystem_updates"):
            messages.info(request, _("Queued Update All Taxsystem"))
            tasks.update_all_taxsytem.apply_async(
                kwargs={"force_refresh": force_refresh}, priority=7
            )
    context = {
        "corporation_id": corporation_id,
        "title": _("Tax System Superuser Administration"),
    }
    return render(request, "taxsystem/admin.html", context=context)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
def administration(request: WSGIRequest, corporation_id: int):
    """Manage View"""
    context = {
        "corporation_id": corporation_id,
        "title": _("Administration"),
        "forms": {
            "accept_request": forms.PaymentAcceptForm(),
            "reject_request": forms.PaymentRejectForm(),
            "add_request": forms.PaymentAddForm(),
            "payment_delete_request": forms.PaymentDeleteForm(),
            "undo_request": forms.PaymentUndoForm(),
            "switchuser_request": forms.TaxSwitchUserForm(),
            "delete_request": forms.MemberDeleteForm(),
        },
    }
    context = add_info_to_context(request, context)

    return render(request, "taxsystem/manage.html", context=context)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
def manage_filter(request: WSGIRequest, corporation_id: int):
    """Manage View"""
    owner, perms = get_manage_corporation(request, corporation_id)

    filter_sets = owner.ts_filter_set.all()
    context = {
        "corporation_id": corporation_id,
        "filter_sets": filter_sets,
        "title": _("Manage Filters"),
        "forms": {
            "filter": forms.AddJournalFilterForm(queryset=owner.ts_filter_set.all()),
            "filter_set": forms.CreateFilterSetForm(),
            "delete_request": forms.MemberDeleteForm(),
        },
    }
    if perms is False:
        messages.error(
            request, _("You do not have permission to manage this corporation.")
        )
        return redirect("taxsystem:index")

    with transaction.atomic():
        form_add = forms.AddJournalFilterForm(
            data=request.POST, queryset=owner.ts_filter_set.all()
        )
        form_set = forms.CreateFilterSetForm(data=request.POST)

        if form_add.is_valid():
            queryset = form_add.cleaned_data["filter_set"]
            filter_type = form_add.cleaned_data["filter_type"]
            value = form_add.cleaned_data["value"]
            try:
                JournalFilter.objects.create(
                    filter_set=queryset,
                    filter_type=filter_type,
                    value=value,
                )
            except IntegrityError:
                messages.error(request, _("A filter with this name already exists."))
                return redirect(
                    "taxsystem:manage_filter", corporation_id=corporation_id
                )
            except Exception as e:  # pylint: disable=broad-except
                messages.error(
                    request, _("Something went wrong, please try again later.")
                )
                logger.error("Error creating journal filter: %s", e)
                return redirect(
                    "taxsystem:manage_filter", corporation_id=corporation_id
                )

        if form_set.is_valid():
            name = form_set.cleaned_data["name"]
            description = form_set.cleaned_data["description"]
            try:
                JournalFilterSet.objects.create(
                    owner=owner,
                    name=name,
                    description=description,
                )
            except IntegrityError:
                messages.error(
                    request, _("A filter set with this name already exists.")
                )
                return redirect(
                    "taxsystem:manage_filter", corporation_id=corporation_id
                )
            except Exception as e:  # pylint: disable=broad-except
                messages.error(
                    request, _("Something went wrong, please try again later.")
                )
                logger.error("Error creating journal filter set: %s", e)
                return render(request, "taxsystem/manage-filter.html", context=context)

    return render(request, "taxsystem/manage-filter.html", context=context)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
def switch_filterset(request: WSGIRequest, corporation_id: int, filter_set_id: int):
    """Deactivate Filter Set View"""
    owner, perms = get_manage_corporation(request, corporation_id)

    if perms is False:
        messages.error(
            request, _("You do not have permission to manage this corporation.")
        )
        return redirect("taxsystem:index")

    filter_set = get_object_or_404(owner.ts_filter_set, id=filter_set_id)
    filter_sets = owner.ts_filter_set.all()

    filter_set.enabled = not filter_set.enabled
    filter_set.save()

    context = {
        "corporation_id": corporation_id,
        "filter_sets": filter_sets,
        "forms": {
            "filter": forms.AddJournalFilterForm(queryset=owner.ts_filter_set.all()),
            "filter_set": forms.CreateFilterSetForm(),
        },
        "title": _("Deactivate Filter Set"),
    }
    context = add_info_to_context(request, context)

    messages.success(
        request, _(f"Filter set switched to {filter_set.enabled} successfully.")
    )
    return redirect("taxsystem:manage_filter", corporation_id=corporation_id)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
def delete_filterset(request: WSGIRequest, corporation_id: int, filter_set_id: int):
    """Delete Filter Set View"""
    owner, perms = get_manage_corporation(request, corporation_id)

    if perms is False:
        messages.error(
            request, _("You do not have permission to manage this corporation.")
        )
        return redirect("taxsystem:index")

    filter_set = get_object_or_404(owner.ts_filter_set, id=filter_set_id)
    filter_sets = owner.ts_filter_set.all()

    filter_set.delete()
    msg = _(f"{filter_set.name} from {owner.name} deleted")
    AdminLogs(
        user=request.user,
        owner=owner,
        action=AdminLogs.Actions.DELETE,
        comment=msg,
    ).save()
    messages.success(request, _("Filter set deleted successfully."))

    context = {
        "corporation_id": corporation_id,
        "filter_sets": filter_sets,
        "forms": {
            "filter": forms.AddJournalFilterForm(queryset=owner.ts_filter_set.all()),
            "filter_set": forms.CreateFilterSetForm(),
        },
        "title": _("Delete Filter Set"),
    }
    context = add_info_to_context(request, context)

    return redirect("taxsystem:manage_filter", corporation_id=corporation_id)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def delete_filter(request: WSGIRequest, corporation_id: int, filter_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    form = forms.FilterDeleteForm(data=request.POST)
    if form.is_valid():
        filter_obj = JournalFilter.objects.get(filter_set__owner=corp, pk=filter_pk)
        if filter_obj:
            msg = _(
                f"{filter_obj.filter_type}({filter_obj.value}) from {filter_obj.filter_set} deleted - {form.cleaned_data['delete_reason']}"
            )
            filter_obj.delete()
            AdminLogs(
                user=request.user,
                owner=corp,
                action=AdminLogs.Actions.DELETE,
                comment=msg,
            ).save()
            return JsonResponse(
                data={"success": True, "message": msg}, status=200, safe=False
            )
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
def edit_filterset(request: WSGIRequest, corporation_id: int, filter_set_id: int):
    """Edit Filter Set View"""
    owner, perms = get_manage_corporation(request, corporation_id)

    if perms is False:
        messages.error(
            request, _("You do not have permission to manage this corporation.")
        )
        return redirect("taxsystem:index")

    edit_set = get_object_or_404(owner.ts_filter_set, id=filter_set_id)
    filter_sets = owner.ts_filter_set.all()

    if request.method == "POST":
        form = forms.EditFilterSetForm(request.POST, instance=edit_set)
        if form.is_valid():
            form.save()
            messages.success(request, _("Filter set updated successfully."))
            return redirect("taxsystem:manage_filter", corporation_id=corporation_id)
    else:
        form = forms.EditFilterSetForm(instance=edit_set)

    context = {
        "corporation_id": corporation_id,
        "filter_sets": filter_sets,
        "forms": {
            "edit_filter_set": form,
        },
        "title": _("Edit Filter Set"),
    }
    context = add_info_to_context(request, context)

    return render(request, "taxsystem/manage-filter.html", context=context)


@login_required
@permission_required("taxsystem.basic_access")
def payments(request: WSGIRequest, corporation_id: int):
    """Payments View"""
    perms = get_corporation(request, corporation_id)

    if perms is None:
        messages.error(request, _("No Corporation found."))

    corporations = OwnerAudit.objects.visible_to(request.user)

    context = {
        "corporation_id": corporation_id,
        "title": _("Payments"),
        "forms": {
            "add_request": forms.PaymentAddForm(),
            "payment_delete_request": forms.PaymentDeleteForm(),
            "accept_request": forms.PaymentAcceptForm(),
            "reject_request": forms.PaymentRejectForm(),
            "undo_request": forms.PaymentUndoForm(),
        },
        "corporations": corporations,
    }
    context = add_info_to_context(request, context)

    return render(request, "taxsystem/payments.html", context=context)


@login_required
@permission_required("taxsystem.basic_access")
def own_payments(request: WSGIRequest, corporation_id=None):
    """Own Payments View"""
    if corporation_id is None:
        corporation_id = request.user.profile.main_character.corporation_id

    corporations, perms = get_manage_corporation(request, corporation_id)

    if corporations is None:
        messages.error(request, _("No Corporation found."))

    if perms is False:
        messages.error(request, _("Permission Denied"))
        return redirect("taxsystem:index")

    corporations = OwnerAudit.objects.visible_to(request.user)

    context = {
        "corporation_id": corporation_id,
        "title": _("Own Payments"),
        "corporations": corporations,
    }
    context = add_info_to_context(request, context)

    return render(request, "taxsystem/own-payments.html", context=context)


@login_required
@permission_required("taxsystem.basic_access")
def faq(request: WSGIRequest, corporation_id: int):
    """Payments View"""
    corporations = OwnerAudit.objects.visible_to(request.user)

    context = {
        "corporation_id": corporation_id,
        "title": _("FAQ"),
        "corporations": corporations,
    }
    context = add_info_to_context(request, context)

    return render(request, "taxsystem/faq.html", context=context)


@login_required
@permission_required("taxsystem.basic_access")
def account(request: WSGIRequest, character_id=None):
    """Account View"""
    if character_id is None:
        character_id = request.user.profile.main_character.character_id
    logger.error(f"Character ID not provided, using main character ID: {character_id}")

    user_profile = UserProfile.objects.filter(
        main_character__character_id=character_id
    ).first()

    if not user_profile:
        messages.error(request, _("No User found."))
        return redirect("taxsystem:index")

    try:
        corporation_id = user_profile.main_character.corporation_id
        owner, perms = get_manage_corporation(request, corporation_id)
        perms = perms or get_character_permissions(request, character_id)
    except AttributeError:
        messages.error(request, _("User has no main character set."))
        return redirect("taxsystem:index")

    payment_user = PaymentSystem.objects.filter(
        user__profile=user_profile,
        owner=owner,
    ).first()

    if not payment_user:
        messages.error(request, _("No Payment System User found."))
        return redirect("taxsystem:index")

    if owner is None:
        messages.error(request, _("Corporation not Found"))
        return redirect("taxsystem:index")

    if perms is False:
        messages.error(request, _("Permission Denied"))
        return redirect("taxsystem:index")

    try:
        member = owner.ts_members.get(character_id=character_id)
    except owner.ts_members.model.DoesNotExist:
        member = None

    context = {
        "title": _("Account"),
        "character_id": character_id,
        "corporation_id": corporation_id,
        "account": {
            "name": payment_user.name,
            "corporation": owner,
            "status": payment_user.Status(payment_user.status).html(text=True),
            "deposit": (
                payment_user.deposit_html
                if payment_user.status != PaymentSystem.Status.MISSING
                else "N/A"
            ),
            "has_paid": (
                payment_user.has_paid_icon(badge=True, text=True)
                if payment_user.status != PaymentSystem.Status.MISSING
                else "N/A"
            ),
            "last_paid": (
                payment_user.last_paid
                if payment_user.status != PaymentSystem.Status.MISSING
                else "N/A"
            ),
            "joined": member.joined if member else "N/A",
            "last_login": member.logon if member else "N/A",
        },
    }
    context = add_info_to_context(request, context)

    return render(request, "taxsystem/account.html", context=context)


@login_required
@permission_required("taxsystem.create_access")
@token_required(scopes=OwnerAudit.get_esi_scopes())
def add_corp(request, token):
    char = get_object_or_404(EveCharacter, character_id=token.character_id)
    corp, __ = EveCorporationInfo.objects.get_or_create(
        corporation_id=char.corporation_id,
        defaults={
            "member_count": 0,
            "corporation_ticker": char.corporation_ticker,
            "corporation_name": char.corporation_name,
        },
    )

    owner, created = OwnerAudit.objects.update_or_create(
        corporation=corp,
        defaults={
            "name": corp.corporation_name,
            "active": True,
        },
    )

    if created:
        AdminLogs(
            user=request.user,
            owner=owner,
            action=AdminLogs.Actions.ADD,
            comment=_("Added to Tax System"),
        ).save()

    tasks.update_corporation.apply_async(
        args=[owner.pk], kwargs={"force_refresh": True}, priority=6
    )
    msg = _("{corporation_name} successfully added/updated to Tax System").format(
        corporation_name=corp.corporation_name,
    )
    messages.info(request, msg)
    return redirect("taxsystem:index")


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def approve_payment(request: WSGIRequest, corporation_id: int, payment_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    try:
        with transaction.atomic():
            form = forms.PaymentAcceptForm(data=request.POST)
            if form.is_valid():
                reason = form.cleaned_data["accept_info"]
                payment = Payments.objects.get(account__owner=corp, pk=payment_pk)
                if payment.is_pending or payment.is_needs_approval:
                    msg = _(
                        "Payment ID: {pid} - Amount: {amount} - Name: {name} approved"
                    ).format(
                        pid=payment.pk,
                        amount=intcomma(payment.amount),
                        name=payment.name,
                    )
                    payment.request_status = Payments.RequestStatus.APPROVED
                    payment.reviser = request.user.profile.main_character.character_name
                    payment.save()

                    payment_account = PaymentSystem.objects.get(
                        owner=corp, user=payment.account.user
                    )
                    payment_account.deposit += payment.amount
                    payment_account.save()
                    PaymentHistory(
                        user=request.user,
                        payment=payment,
                        action=PaymentHistory.Actions.STATUS_CHANGE,
                        comment=reason,
                        new_status=Payments.RequestStatus.APPROVED,
                    ).save()
                    return JsonResponse(
                        data={"success": True, "message": msg}, status=200, safe=False
                    )
    except IntegrityError:
        msg = _("Transaction failed. Please try again.")
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def undo_payment(request: WSGIRequest, corporation_id: int, payment_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    try:
        with transaction.atomic():
            form = forms.PaymentUndoForm(data=request.POST)
            if form.is_valid():
                reason = form.cleaned_data["undo_reason"]
                payment = Payments.objects.get(account__owner=corp, pk=payment_pk)
                if payment.is_approved or payment.is_rejected:
                    msg = _(
                        "Payment ID: {pid} - Amount: {amount} - Name: {name} undone"
                    ).format(
                        pid=payment.pk,
                        amount=intcomma(payment.amount),
                        name=payment.name,
                    )
                    # Ensure that the payment is not rejected
                    if not payment.is_rejected:
                        payment_account = PaymentSystem.objects.get(
                            owner=corp, user=payment.account.user
                        )
                        payment_account.deposit -= payment.amount
                        payment_account.save()
                    payment.request_status = Payments.RequestStatus.PENDING
                    payment.reviser = ""
                    payment.save()
                    PaymentHistory(
                        user=request.user,
                        payment=payment,
                        action=PaymentHistory.Actions.STATUS_CHANGE,
                        comment=reason,
                        new_status=Payments.RequestStatus.PENDING,
                    ).save()
                    return JsonResponse(
                        data={"success": True, "message": msg}, status=200, safe=False
                    )
    except IntegrityError:
        msg = _("Transaction failed. Please try again.")
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def reject_payment(request: WSGIRequest, corporation_id: int, payment_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    try:
        with transaction.atomic():
            form = forms.PaymentRejectForm(data=request.POST)
            if form.is_valid():
                reason = form.cleaned_data["reject_reason"]
                payment = Payments.objects.get(account__owner=corp, pk=payment_pk)
                if payment.is_pending or payment.is_needs_approval:
                    payment.request_status = Payments.RequestStatus.REJECTED
                    payment.reviser = request.user.profile.main_character.character_name
                    payment.save()

                    payment_account = PaymentSystem.objects.get(
                        owner=corp, user=payment.account.user
                    )
                    payment_account.save()
                    msg = _(
                        "Payment ID: {pid} - Amount: {amount} - Name: {name} rejected"
                    ).format(
                        pid=payment.pk,
                        amount=intcomma(payment.amount),
                        name=payment.name,
                    )

                    PaymentHistory(
                        user=request.user,
                        payment=payment,
                        action=PaymentHistory.Actions.STATUS_CHANGE,
                        comment=reason,
                        new_status=Payments.RequestStatus.REJECTED,
                    ).save()
                    return JsonResponse(
                        data={"success": True, "message": msg}, status=200, safe=False
                    )
    except IntegrityError:
        msg = _("Transaction failed. Please try again.")
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def delete_payment(request: WSGIRequest, corporation_id: int, payment_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    try:
        with transaction.atomic():
            form = forms.PaymentDeleteForm(data=request.POST)
            if form.is_valid():
                reason = form.cleaned_data["delete_reason"]
                payment = Payments.objects.get(account__owner=corp, pk=payment_pk)

                if payment.entry_id != 0:  # Prevent deletion of ESI imported payments
                    msg = _(
                        "Payment ID: {pid} - Amount: {amount} - Name: {name} deletion failed - ESI imported payments cannot be deleted"
                    ).format(
                        pid=payment.pk,
                        amount=intcomma(payment.amount),
                        name=payment.name,
                    )
                    return JsonResponse(
                        data={"success": False, "message": msg}, status=400, safe=False
                    )

                msg = _(
                    "Payment ID: {pid} - Amount: {amount} - Name: {name} deleted - {reason}"
                ).format(
                    pid=payment.pk,
                    amount=intcomma(payment.amount),
                    name=payment.name,
                    reason=reason,
                )

                # Refund if approved
                if payment.is_approved:
                    payment_user = PaymentSystem.objects.get(
                        owner=corp, user=payment.account.user
                    )
                    payment_user.deposit -= payment.amount
                    payment_user.save()
                # Delete Payment
                payment.delete()

                # Log Payment Action
                AdminLogs(
                    user=request.user,
                    owner=corp,
                    action=AdminLogs.Actions.DELETE,
                    comment=msg,
                ).save()

                return JsonResponse(
                    data={"success": True, "message": msg}, status=200, safe=False
                )
    except IntegrityError:
        msg = _("Transaction failed. Please try again.")
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def add_payment(request: WSGIRequest, corporation_id: int, payment_system_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    try:
        with transaction.atomic():
            form = forms.PaymentAddForm(data=request.POST)
            if form.is_valid():
                amount = form.cleaned_data["amount"]
                reason = form.cleaned_data["add_reason"]
                payment_account = PaymentSystem.objects.get(
                    owner=corp, pk=payment_system_pk
                )

                payment = Payments(
                    name=payment_account.user.username,
                    entry_id=0,  # Manual Entry
                    amount=amount,
                    account=payment_account,
                    date=timezone.now(),
                    reason=reason,
                    request_status=Payments.RequestStatus.APPROVED,
                    reviser=request.user.username,
                    corporation_id=corporation_id,
                )
                payment.save()
                payment_account.deposit += amount
                payment_account.save()

                msg = _(
                    "Payment ID: {pid} - Amount: {amount} - Name: {name} added"
                ).format(
                    pid=payment.pk,
                    amount=intcomma(payment.amount),
                    name=payment.name,
                )

                PaymentHistory(
                    user=request.user,
                    payment=payment,
                    action=PaymentHistory.Actions.PAYMENT_ADDED,
                    comment=reason,
                    new_status=Payments.RequestStatus.APPROVED,
                ).save()

                # Log Admin Action
                AdminLogs(
                    user=request.user,
                    owner=corp,
                    action=AdminLogs.Actions.ADD,
                    comment=msg,
                ).save()

                return JsonResponse(
                    data={"success": True, "message": msg}, status=200, safe=False
                )
    except IntegrityError:
        msg = _("Transaction failed. Please try again.")
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def switch_user(request: WSGIRequest, corporation_id: int, payment_system_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    try:
        with transaction.atomic():
            form = forms.TaxSwitchUserForm(data=request.POST)
            if form.is_valid():
                payment_system = PaymentSystem.objects.get(
                    owner=corp, pk=payment_system_pk
                )
                if payment_system.is_active:
                    payment_system.status = PaymentSystem.Status.DEACTIVATED
                    msg = _("Payment System User: %s deactivated") % payment_system.name
                else:
                    payment_system.status = PaymentSystem.Status.ACTIVE
                    msg = _("Payment System User: %s activated") % payment_system.name

                AdminLogs(
                    user=request.user,
                    owner=corp,
                    action=AdminLogs.Actions.CHANGE,
                    comment=msg,
                ).save()
                payment_system.save()
            return JsonResponse(
                data={"success": True, "message": msg}, status=200, safe=False
            )
    except IntegrityError:
        msg = _("Transaction failed. Please try again.")
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@csrf_exempt
def update_tax_amount(request: WSGIRequest, corporation_id: int):
    if request.method == "POST":
        value = float(request.POST.get("value"))
        msg = _("Please enter a valid number")
        try:
            if value < 0:
                return JsonResponse({"message": msg}, status=400)
        except ValueError:
            return JsonResponse({"message": msg}, status=400)

        corp = get_corporation(request, corporation_id)

        perms = get_manage_permission(request, corporation_id)

        if not perms:
            return JsonResponse({"message": _("Permission Denied")}, status=403)

        try:
            corp.tax_amount = value
            corp.save()
            msg = _(f"Tax Amount from {corp.name} updated to {value}")
            AdminLogs(
                user=request.user,
                owner=corp,
                action=AdminLogs.Actions.CHANGE,
                comment=msg,
            ).save()
        except ValidationError:
            return JsonResponse({"message": msg}, status=400)
        return JsonResponse({"message": msg}, status=200)
    return JsonResponse({"message": _("Invalid request method")}, status=405)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@csrf_exempt
def update_tax_period(request: WSGIRequest, corporation_id: int):
    if request.method == "POST":
        value = int(request.POST.get("value"))
        msg = _("Please enter a valid number")
        try:
            if value < 0:
                return JsonResponse({"message": msg}, status=400)
        except ValueError:
            return JsonResponse({"message": msg}, status=400)

        corp = get_corporation(request, corporation_id)

        perms = get_manage_permission(request, corporation_id)

        if not perms:
            return JsonResponse({"message": _("Permission Denied")}, status=403)

        try:
            corp.tax_period = value
            corp.save()
            msg = _(f"Tax Period from {corp.name} updated to {value}")
            AdminLogs(
                user=request.user,
                owner=corp,
                action=AdminLogs.Actions.CHANGE,
                comment=msg,
            ).save()
        except ValidationError:
            return JsonResponse({"message": msg}, status=400)
        return JsonResponse({"message": msg}, status=200)
    return JsonResponse({"message": _("Invalid request method")}, status=405)


@login_required
@permissions_required(["taxsystem.manage_own_corp", "taxsystem.manage_corps"])
@require_POST
def delete_member(request: WSGIRequest, corporation_id: int, member_pk: int):
    msg = _("Invalid Method")
    corp = get_corporation(request, corporation_id)

    perms = get_manage_permission(request, corporation_id)
    if not perms:
        msg = _("Permission Denied")
        return JsonResponse(
            data={"success": False, "message": msg}, status=403, safe=False
        )

    form = forms.MemberDeleteForm(data=request.POST)
    if form.is_valid():
        reason = form.cleaned_data["delete_reason"]
        member = Members.objects.get(owner=corp, pk=member_pk)
        if member.is_missing:
            msg = _(f"Member {member.character_name} deleted - {reason}")
            member.delete()
            AdminLogs(
                user=request.user,
                owner=corp,
                action=AdminLogs.Actions.DELETE,
                comment=msg,
            ).save()
            return JsonResponse(
                data={"success": True, "message": msg}, status=200, safe=False
            )
    return JsonResponse(data={"success": False, "message": msg}, status=400, safe=False)
