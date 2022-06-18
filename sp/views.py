from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from .forms import *
from .filters import *

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings

from django.contrib.auth.decorators import login_required

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.contrib.auth import authenticate, login

from djmoney.money import Money

# Create your views here.
def indexView(request):
	context = {}
	return render(request, 'main/index01.html', context)

def teacherLoginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			if username == 'admin':
				messages.info(request,'Invalid Credentials')

			else:
				login(request, user)
				return redirect('/')
		else:
			messages.info(request,'Invalid Credentials')


	context = {}
	return render(request, 'login/teacher-login.html', context)

def adminLoginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			if username != 'admin':
				print('Yeah')
				messages.info(request,'Invalid Credentials')

			else:
				login(request, user)
				return redirect('/')

		else:
			messages.info(request,'Invalid Credentials')
	context = {}
	return render(request, 'login/admin-login.html', context)

@login_required(login_url='/')
def registerTeacherView(request):
	if request.method == 'POST':
		teacher_form = RegisterTeacherForm(request.POST)
		teacher_form01 = RegisterTeacherForm01(request.POST)
		if teacher_form.is_valid() and teacher_form01.is_valid():
			teacher_form01.save()
			teacher_form.save()
			username = teacher_form01.cleaned_data['username']
			t = Teacher.objects.last()
			u = User.objects.last()
			t.user = u
			t.save()
			messages.success(request, f'{username} created successfully!')
			return redirect('/register/teacher')
		else:
			messages.info(request, f'Please fill up the form correctly')
	teacher_form = RegisterTeacherForm()
	teacher_form01 = RegisterTeacherForm01()
	context = {'teacher_form':teacher_form, 'teacher_form01':teacher_form01}
	return render(request, 'registration/teacher-registration-form.html', context)

@login_required(login_url='/')
def registerStudentView(request,):
	if request.method == 'POST':
		form = RegisterStudentForm(request.POST)
		if form.is_valid():
			last_name = form.cleaned_data['last_name']
			first_name = form.cleaned_data['first_name']
			form.save()
			messages.success(request, f'{last_name} {first_name} has been registered successfully.')
			return redirect('/register/student/')

	form = RegisterStudentForm()
	context = {'form':form}		
	return render(request, 'registration/student-registration-form.html', context)

@login_required(login_url='/')
def economyView(request):
	e = Economy.objects.all()

	if request.method == 'POST':
		form = EconomyForm(request.POST)
		if form.is_valid():
			teacher = form.cleaned_data['teacher']
			student = form.cleaned_data['student']


			print('Valid form')
			if Economy.objects.filter(teacher=teacher):
				e = Economy.objects.get(teacher=teacher)
				print('Teacher already exists')
			else:
				print('Teacher added')
				Economy(teacher=teacher).save()
				e = Economy.objects.get(teacher=teacher)
			sid = student.values_list('id', flat=True)
			print(f'sid: {sid.all()}')
			for i in sid.all():
				print(f'Loop {i}')
				if StudentEconomy.objects.filter(name=student.get(id=i), teacher=teacher):
					print('Student already exists')

				else:
					StudentEconomy(name=student.get(id=i), teacher=teacher).save()
					se = StudentEconomy.objects.get(name=student.get(id=i), teacher=teacher)
					se.status='Active'
					se.save()
					print(se.status)
					e.student.add(StudentEconomy.objects.get(name=student.get(id=i), teacher=teacher))
					e.save()
					print('Student Added')
					messages.success(request, f'Student: {student.get(id=i)} successfully added to economy')
			return redirect('/economy/')
		else:
			print('invalid form')

	form = EconomyForm()
	context = {'form':form, 'e':e}
	return render(request, 'economy/economy.html', context)

@login_required(login_url='/')
def setActive(request, pk):
	se = StudentEconomy.objects.get(id=pk)
	se.status = 'Active'
	se.save()
	messages.success(request, f'{se.name} set to active')
	return redirect('/economy/')

@login_required(login_url='/')
def setInactive(request, pk):
	se = StudentEconomy.objects.get(id=pk)
	se.status = 'Inactive'
	se.save()
	print(f'Nam: {se.name}')
	print(f'Status {se.status}')
	messages.success(request, f'{se.name} set to inactive')
	return redirect('/economy/')

@login_required(login_url='/')
def accountSettingsView(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Your password was successfully updated!')
			return redirect('/')
		else:
			messages.info(request, 'Please correct the error below.')
	form = PasswordChangeForm(request.user)
	context = {'form':form}
	return render(request, 'settings/account/account-settings.html', context)

@login_required(login_url='/')
def schoolSettingsView(request, user):
	t = Teacher.objects.get(user=user)
	if request.method == 'POST':
		form = SchoolSettingsForm(request.POST, request.FILES)
		if form.is_valid():
			school_name = form.cleaned_data['school_name']
			school_logo = form.cleaned_data['school_logo']
			t.school_name = school_name
			t.school_logo = school_logo
			t.save()
			messages.success(request, 'School Settings successfully updated!')
			return redirect('/')

	form = SchoolSettingsForm()
	context = {'form':form}
	return render(request, 'settings/school/school-settings.html', context)

@login_required(login_url='/')
def jobsView(request, user):
	teacher = Teacher.objects.get(user=user)
	if request.method == 'POST':
		form = CreateJobsForm(request.POST)
		if form.is_valid():
			print('form is valid')
			job = form.cleaned_data['job']
			suggested_per_class = form.cleaned_data['suggested_per_class']
			job_description = form.cleaned_data['job_description']
			salary = form.cleaned_data['salary']
			# student_assigned = form.cleaned_data['student_assigned']
			Job(teacher=teacher, job=job, suggested_per_class=suggested_per_class, job_description=job_description, salary=salary).save()
			
		else:
			messages.success(request, 'Student Already has a job!')

	
	student = StudentEconomy.objects.filter(teacher=teacher)
	j = Job.objects.filter(teacher=teacher)
	form = CreateJobsForm()
	context = {'form':form, 'j':j}
	return render(request, 'rules/jobs/jobs.html', context)


@login_required(login_url='/')
def updateJobsView(request, user, pk):
	jobs = Job.objects.get(id=pk)
	teacher = Teacher.objects.get(user=user)
	form = UpdateJobsForm(teacher, instance=jobs)
	if request.method == 'POST':
		form = UpdateJobsForm(teacher,request.POST, instance=jobs)
		if form.is_valid():
			print('Form is valid')
			job = form.cleaned_data['job']
			suggested_per_class = form.cleaned_data['suggested_per_class']
			salary = form.cleaned_data['salary']
			job_description = form.cleaned_data['job_description']
			student_assigned = form.cleaned_data['student_assigned']

			
			jobs.job = job
			jobs.suggested_per_class = suggested_per_class
			jobs.salary_before = jobs.salary
			jobs.salary = salary
			jobs.job_description = job_description
			jobs.student_assigned.set(student_assigned)
			jobs.save()

			for i in jobs.student_assigned.all():

				isMax = i.balance + salary
				if isMax > Money(100, 'PHP'):
					jobs.student_assigned.remove(i)
					messages.info(request, f'Student: {i.name} reahed maximun balance ₱100')
				else:
					i.jobs = job
					i.balance = i.balance + salary
					i.salary = salary
					i.save()

			messages.success(request, 'Jobs successfully updated!')
			return redirect(f'/rules/jobs/{user}/')

		else:
			print('Invalid Form')
	
	context = {'form':form,'jobs':jobs}
	return render(request, 'rules/jobs/update-jobs.html', context)


@login_required(login_url='/')
def deleteJobsView(request, user, pk):
	jobs = Job.objects.get(id=pk)
	if request.method == 'POST':

		for i in jobs.student_assigned.all():
			i.jobs = ''
			i.salary = 0
			i.save()

		jobs.delete()
		messages.success(request, 'Job successfully deleted!')
		return redirect(f'/rules/jobs/{user}/')
	context = {'jobs':jobs}
	return render(request, 'rules/jobs/delete-jobs.html', context)


@login_required(login_url='/')
def opportunitiesView(request, user):
	teacher = Teacher.objects.get(user=user)
	if request.method == 'POST':
		form = CreateOpportunitiesForm(request.POST)
		if form.is_valid():
			activity = form.cleaned_data['activity']
			amount = form.cleaned_data['amount']
			print('Valid')

			Opportunitie(teacher=teacher, activity=activity, amount=amount).save()
			messages.success(request, 'Opportunities successfully added!')
			return redirect(f'/rules/opportunities/{user}/')

	opportunities = Opportunitie.objects.filter(teacher=teacher)
	form = CreateOpportunitiesForm()
	context = {'form':form, 'opportunities':opportunities}
	return render(request, 'rules/opportunities/opportunities.html', context)

@login_required(login_url='/')
def updateOpportunitiesView(request, user, pk):
	opportunities = Opportunitie.objects.get(id=pk)
	teacher = Teacher.objects.get(user=user)

	form = UpdateOpportunitiesForm(teacher,instance=opportunities)
	if request.method == 'POST':
		form = UpdateOpportunitiesForm(teacher, request.POST, instance=opportunities)
		
		if form.is_valid():

			activity = form.cleaned_data['activity']
			amount = form.cleaned_data['amount']
			student = form.cleaned_data['student']
			amount_before = opportunities.amount

			opportunities.activity = activity
			opportunities.amount_before = amount_before
			print(opportunities.amount_before)
			opportunities.amount = amount
			print(opportunities.amount)
			opportunities.student.set(student)
			opportunities.save()

			for i in opportunities.student.all():
				isMax = i.balance + amount
				if isMax > Money(100, 'PHP'):
					opportunities.student.remove(i)
					messages.info(request, f'Student: {i.name} reahed maximun balance ₱100')
				else:
					i.balance = i.balance + amount
					i.save()

			messages.success(request, f'{opportunities.activity} successfully updated!')
			return redirect(f'/rules/opportunities/{user}')

	context = {'form':form, 'opportunities':opportunities}
	return render(request, 'rules/opportunities/update-opportunities.html', context)

@login_required(login_url='/')
def deleteOpportunitiesView(request, user, pk):
	opportunities = Opportunitie.objects.get(id=pk)
	if request.method == 'POST':
		opportunities.delete()
		messages.success(request, f'{opportunities.activity} successfully deleted!')
		return redirect(f'/rules/opportunities/{user}/')
	context = {'opportunities':opportunities}
	return render(request, 'rules/opportunities/delete-opportunities.html', context)

@login_required(login_url='/')
def houseRulesView(request, user):
	teacher = Teacher.objects.get(user=user)
	if request.method == 'POST':
		form = CreateHouseRulesForm(request.POST)
		if form.is_valid():
			rule = form.cleaned_data['rule']
			fine = form.cleaned_data['fine']

			HouseRule(teacher=teacher, rule=rule, fine=fine).save()
			messages.success(request, 'House Rules successfully added!')
			return redirect(f'/rules/house-rules/{user}/')

	h = HouseRule.objects.filter(teacher=teacher)
	form = CreateHouseRulesForm()
	context = {'form':form, 'h':h}
	return render(request, 'rules/house-rules/house-rules.html', context)

@login_required(login_url='/')
def updateHouseRulesView(request, user, pk):
	h = HouseRule.objects.get(id=pk)
	teacher = Teacher.objects.get(user=user)
	form = UpdateHouseRulesForm(teacher, instance=h)
	if request.method == 'POST':
		form = UpdateHouseRulesForm(teacher,request.POST, instance=h)
		if form.is_valid():
			rule = form.cleaned_data['rule']
			student = form.cleaned_data['student']
			fine = form.cleaned_data['fine']
			fine_before = h.fine_before
			h.rule = rule
			h.fine_before = h.fine
			h.fine = fine
			h.student.set(student)
			h.save()

			for i in h.student.all():
				print(f'Fine {fine}')
				print(f'Fine Before: {fine_before}')
				print(f'Fine {(fine_before - fine)}')
				i.spend = i.spend + abs(fine_before - fine)
				i.balance = i.balance - abs(fine_before - fine)
				i.save()
				print(f'Student: {i.name} Balance:{i.balance}')



			messages.success(request, f'{h.rule} successfully updated!')
			return redirect(f'/rules/house-rules/{user}/')

	context = {'form':form, 'h':h}
	return render(request, 'rules/house-rules/update-house-rules.html', context)

@login_required(login_url='/')
def updateStudentHouseRulesView(request, user, pk):
	h = HouseRule.objects.get(id=pk)
	teacher = Teacher.objects.get(user=user)
	form = UpdateHouseRulesForm(teacher,instance=h)

	if request.method == 'POST':
		form = UpdateHouseRulesForm(teacher,request.POST, instance=h)
		if form.is_valid():
			student = form.cleaned_data['student']

			sid = student.values_list('id', flat=True)
			h.student.set(student)
			h.save()

			print(h.student.all())
			for i in sid.all():
				for j in h.student.all():
					print(f'J: {j}')
					print(f'I: {StudentEconomy.objects.get(id=i).name}')
					if j == StudentEconomy.objects.get(id=i).name:
						print('Yeah Yeah')
				else:	
					print('Noononon')
					h.student.set(StudentEconomy.objects.get(id=i))
					h.save()
					s = StudentEconomy.objects.get(id=i)
					s.spend = s.spend + fine
					s.balance = s.balance - fine
					s.save()
					print(f'Student: {se.name} Success')

			messages.success(request, f'{h.rule} successfully updated!')
			return redirect(f'/rules/house-rules/{user}/')


	context = {'form':form, 'h':h}
	return render(request, 'rules/house-rules/update-house-rules.html', context)

@login_required(login_url='/')
def deleteHouseRulesView(request, user, pk):
	h = HouseRule.objects.get(id=pk)
	if request.method == 'POST':
		h.delete()
		messages.success(request, f'{h.rule} successfully deleted!')
		return redirect(f'/rules/house-rules/{user}')
	context = {'h':h}
	return render(request, 'rules/house-rules/delete-house-rules.html', context)


@login_required(login_url='/')
def rentView(request, user):
	teacher = Teacher.objects.get(user=user)
	if request.method == 'POST':
		form = RentForm(request.POST)
		if form.is_valid():
			sdate = form.cleaned_data['sdate']
			edate = form.cleaned_data['edate']
			posting = form.cleaned_data['posting']
			amount = form.cleaned_data['amount']
			Rent(teacher=teacher, start_date=sdate, end_date=edate, posting=posting, amount=amount).save()
			
			se = StudentEconomy.objects.all().filter(teacher=teacher)

			for i in se:
				i.balance = i.balance - amount
				i.spend = i.spend + amount
				i.save()
				print('Rent Success')

			messages.success(request, 'Rent added successfully!')
			return redirect(f'/rules/rent/{user}')
		else:
			messages.info(request, 'Please fill up the form correctly')
			return redirect(f'/rules/rent/{user}')
	form = RentForm()
	context = {'form':form}
	return render(request, 'rules/rent/rent.html', context)


@login_required(login_url='/')
def studentMonitoringView(request, user):
	teacher = Teacher.objects.get(user=user)
	se = StudentEconomy.objects.filter(teacher=teacher)
	context = {'se':se}
	return render(request, 'monitoring/student/student.html', context)

@login_required(login_url='/')
def itemStoreView(request, user):
	teacher = Teacher.objects.get(user=user)

	if request.method == 'POST':
		form = ItemStoreForm(teacher, request.POST)
		if form.is_valid():
			print('Form is Valid')

			item1 = form.cleaned_data['item']
			price = form.cleaned_data['price']
			student = form.cleaned_data['student']

			ItemStore(teacher=teacher, item=item1, price=price).save()
			item = ItemStore.objects.all().last()
			item.student.set(student)
			item.save()

			for i in item.student.all():
				if i.balance < price:
					item.student.remove(i)
					messages.info(request, f'Student: {i.name} does not have enough balance!')
				else:	
					i.purchased = f'{i.purchased} {item1},'
					i.balance = i.balance - price
					i.spend = i.spend + price
					i.save()	

			messages.success(request, 'Item added successfully!')
			return redirect(f'/item-store/{user}/')
		else:
			print('Invalid Form')

	item = ItemStore.objects.filter(teacher=teacher)
	form = ItemStoreForm(teacher)
	context = {'form':form, 'item':item}
	return render(request, 'item_store/item-store.html', context)

@login_required(login_url='/')
def deleteItemStoreView(request, user, pk):
	item = ItemStore.objects.get(id=pk)
	if request.method == 'POST':
		item.delete()
		messages.success(request, f'{item.item} successfully deleted!')
		return redirect(f'/item-store/{user}/')
	context = {'item':item}
	return render(request, 'item_store/delete-item-store.html', context)

@login_required(login_url='/')
def billView(request, user):
	teacher = Teacher.objects.get(user=user)

	if request.method == 'POST':
		form = BillForm(teacher, request.POST)

		if form.is_valid():
			print('Form is valid')

			name = form.cleaned_data['name']
			value = form.cleaned_data['value']
			count = form.cleaned_data['count']
			

			if value == '10':
				value = Money(10, 'PHP')
			if value == '20':
				value = Money(20, 'PHP')
			if value == '50':
				value = Money(50, 'PHP')
			if value == '100':
				value = Money(100, 'PHP')


			total_value = value * count

			print(f'Name: {name}')
			print(f'Value: {value}')
			print(f'Count: {count}')
			print(f'Total Value: {total_value}')

			se = StudentEconomy.objects.get(name=name.name.id, teacher=teacher)
			if se.balance < total_value:
				messages.info(request,f'Student: {se.name} has insuffiecient balance!')
			else:

				Bill(teacher=teacher, name=name, value=value, count=count, total_value=total_value).save()

				se.balance = se.balance - total_value
				se.spend = se.spend + total_value
				se.save()
				messages.success(request, 'Bill successfully added!')
				print(f'Student: {se} balance:{se.balance}')
				return redirect(f'/materials/bill/{user}')

				print(f'Value {value}')

		else:
			print('Invalid Form')

	bill = Bill.objects.filter(teacher=teacher)
	form = BillForm(teacher)
	context = {'form':form, 'bill':bill}
	return render(request, 'materials/bill/bill.html', context)

@login_required(login_url='/')
def moneyCirculationView(request, user):
	teacher = Teacher.objects.get(user=user)
	bill = Bill.objects.filter(teacher=teacher)
	total = 0
	for i in bill:
		total += i.total_value
	context = {'total':total}
	return render(request, 'materials/bill/money-circulation.html', context)

@login_required(login_url='/')
def printBillView(request, user, pk):
	bill = Bill.objects.get(id=pk)
	count_range = []
	for i in range(bill.count):
		count_range.append(i)

	context = {'bill':bill, 'count_range':count_range}
	return render(request, 'materials/bill/print-bill.html', context)


@login_required(login_url='/')
def printTenBillsView(request, user, pk):
	ten = [0,1,2,3,4,5,6,7,8,9]
	bill = Bill.objects.get(id=pk)

	context = {'bill':bill, 'ten':ten}
	return render(request, 'materials/bill/print-ten-bills.html', context)

@login_required(login_url='/')
def printTwentyBillsView(request, user, pk):
	twenty = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
	bill = Bill.objects.get(id=pk)

	context = {'bill':bill, 'twenty':twenty}
	return render(request, 'materials/bill/print-twenty-bills.html', context)

@login_required(login_url='/')
def printJobsView(request, user):
	teacher = Teacher.objects.get(user=user)
	jobs = Job.objects.filter(teacher=teacher)
	context = {'jobs':jobs}
	return render(request, 'materials/jobs/print-jobs.html', context)

@login_required(login_url='/')
def printBusinessEnvelopeView(request, user):
	context = {}
	return render(request, 'materials/business_envelopes/print-business-envelope.html', context)

@login_required(login_url='/')
def printHouseRulesView(request, user):
	teacher = Teacher.objects.get(user=user)
	h = HouseRule.objects.filter(teacher=teacher)
	context = {'h':h}
	return render(request, 'materials/rules/print-house-rules.html', context)

@login_required(login_url='/')
def certificateView(request, user):
	teacher = Teacher.objects.get(user=user)

	if request.method == 'POST':
		form = CertificateForm(teacher, request.POST)
		if form.is_valid():
			print('Form is valid')
			student = form.cleaned_data['student']
			date = form.cleaned_data['date']
			Certificate(teacher=teacher, student=student, date=date).save()

		else:
			print('Invalid form')

	form = CertificateForm(teacher)
	context = {'form':form}
	return render(request, 'materials/certificate/certificate.html', context)

@login_required(login_url='/')
def printCertificateView(request, user):
	c = Certificate.objects.all().last()
	context = {'c':c}
	return render(request, 'materials/certificate/print-certificate.html', context)

@login_required(login_url='/')
def debriefingSessionView(request, user):
	teacher = Teacher.objects.get(user=user)
	
	if request.method == 'POST':
		form = DebriefingSessionForm(request.POST)
		if form.is_valid():
			question = form.cleaned_data['question']
			DebriefingSession(teacher=teacher, question=question).save()
			messages.success(request, 'Question created successfully!')

	d = DebriefingSession.objects.filter(teacher=teacher)
	form = DebriefingSessionForm()
	context = {'form':form, 'd':d}

	return render(request, 'materials/debriefing_session/debriefing-session.html', context)

@login_required(login_url='/')
def updateDebriefingSessionView(request, user, pk):
	d = DebriefingSession.objects.get(id=pk)
	form = DebriefingSessionForm(instance=d)
	if request.method == 'POST':
		form = DebriefingSessionForm(request.POST, instance=d)
		if form.is_valid():
			form.save()
			messages.success(request, 'Question successfully updated!')
			return redirect(f'/materials/debriefing-session/{user}/')
	
	context = {'form':form, 'd':d}
	return render(request, 'materials/debriefing_session/update-debriefing-session.html', context)

@login_required(login_url='/')
def deleteDebriefingSessionView(request, user, pk):
	d = DebriefingSession.objects.get(id=pk)
	if request.method == 'POST':
		d.delete()
		messages.success(request, f'{d.question} successfully deleted!')
		return redirect(f'/materials/debriefing-session/{user}')
	context = {'d':d}
	return render(request, 'materials/debriefing_session/delete-debriefing-session.html', context)

@login_required(login_url='/')
def printDebriefingSessionView(request, user):
	teacher = Teacher.objects.get(user=user)
	d = DebriefingSession.objects.filter(teacher=teacher)
	context = {'d':d}
	return render(request,'materials/debriefing_session/print-debriefing-session.html', context)


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "passwords/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						print(f'Email: {user.email}')
						print(f'From: {settings.DEFAULT_FROM_EMAIL}')
						send_mail(subject=subject, message=email, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email], fail_silently=False)
						print('It Worked!')
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="passwords/password_reset.html", context={"password_reset_form":password_reset_form})