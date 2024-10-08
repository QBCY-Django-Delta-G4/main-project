from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from management.forms import *
from management.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError


@login_required(login_url='login')
@permission_required('management.add_doctor', raise_exception=True)
def create_doctor(request:HttpRequest):
    if request.method == 'POST':
        forms = DoctorForm(request.POST, request.FILES)
        if not forms.is_valid():
            return render(request, 'doctor/create_doctor.html', {'forms': forms})
        else:
            forms.save()
            msg = f'دکتر {forms.cleaned_data["first_name"]} {forms.cleaned_data["last_name"]} اضافه شد.'
            messages.success(request, msg)
            return redirect('viewdoctor')
    else:
        forms = DoctorForm()

    return render(request, 'doctor/create_doctor.html', {'forms': forms})


@login_required(login_url='login')
def view_doctor(request:HttpRequest):
    doctors = Doctor.objects.filter(is_deleted=False).order_by('-id')
    context = {
        'doctors': doctors
    }
    return render(request, 'doctor/view_doctor.html', context)



@login_required(login_url='login')
@permission_required('management.add_specialization', raise_exception=True)
def create_specialize(request:HttpRequest):
    if request.method == 'POST':
        forms = SpecializationForm(request.POST)
        if not forms.is_valid():
            return render(request, 'doctor/create_specialize.html', {'forms': forms})

        forms.save()
        msg = f'تخصص {forms.cleaned_data["title"]} اضافه شد.'
        messages.success(request, msg)
        return redirect('viewdoctor')

    else:
        forms = SpecializationForm()

    return render(request, 'doctor/create_specialize.html', {'forms': forms})



@login_required(login_url='login')
@permission_required('management.delete_doctor', raise_exception=True)
def delete_doctor(request:HttpRequest, id):
    doctor = Doctor.objects.get(id=id)
    doctor.is_deleted = True
    doctor.save()
    msg = f'دکتر {doctor.first_name} {doctor.last_name} حذف شد.'
    messages.success(request, msg)
    return redirect("viewdoctor")



@login_required(login_url='login')
@permission_required('management.change_doctor', raise_exception=True)
def edit_doctor(request:HttpRequest, id):
    doctor = Doctor.objects.get(pk=id)
    if request.method == "POST":
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            msg = f'دکتر {doctor.first_name} {doctor.last_name} ویرایش شد.'
            messages.success(request, msg)
            return redirect('viewdoctor')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'doctor/edit_doctor.html', {'forms': form})


@login_required(login_url='login')
def detail_doctor(request: HttpRequest, id):
    doctor = get_object_or_404(Doctor, id=id)
    comments = doctor.comments.filter(is_deleted=False, active=True).order_by('-id')

    score = None
    is_visited = False
    if request.user.is_staff:
        patient = None
    else:
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            patient = None
        reserved_tiems = AvailableTime.objects.filter(doctor=doctor, patient=patient)
        if reserved_tiems:
            is_visited = True
        try:
            score = Rating.objects.get(doctor=doctor, patient=patient)
            score = score.score
        except:
            score = None

    if request.method == "POST":
        btn_submit = request.POST.get('btn-submit')
        if btn_submit == "ثبت امتیاز":
            rate = request.POST.get('rating')
            if rate is not None:
                try:
                    Rating.objects.create(score=int(rate), doctor=doctor, patient=patient)
                    messages.success(request, 'امتیاز شما با موفقیت ثبت شد.')
                except IntegrityError:
                    messages.error(request, 'خطا در ثبت امتیاز. لطفا دوباره امتحان کنید.')
                except Exception as e:
                    messages.error(request, f'خطای ناشناخته{e}')

        elif btn_submit == "ثبت نظر":
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.doctor = doctor
                new_comment.patient = patient
                new_comment.save()
                messages.success(request, 'نظر شما با موفقیت ارسال شد.')

        return redirect('detail_doctor', id=id)

    else:
        comment_form = CommentForm()
        rating_form = RatingForm()

    paginator = Paginator(comments, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    average_score = get_average_rating(id)
    if average_score is None:
        average_score = 0

    if score is None:
        score = 0

    context = {
        'doctor': doctor,
        'page_obj': page_obj,
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'is_admin': request.user.is_staff,
        'score': score,
        'average_score': average_score,
        'is_visited': is_visited
    }
    return render(request, 'doctor/detail_doctor.html', context)



@login_required(login_url='login')
def delete_comment(request:HttpRequest, doctor_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, doctor_id=doctor_id)

    if request.user.is_staff or (comment.patient.user == request.user):
        comment.is_deleted = True
        comment.save()
        messages.success(request, 'نظر با موفقیت حذف شد.')
    else:
        messages.error(request, 'شما مجاز به حذف این نظر نیستید.')

    return redirect('detail_doctor', id=doctor_id)

