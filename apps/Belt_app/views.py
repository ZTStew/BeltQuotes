from django.shortcuts import render, redirect
from .models import User, Quote
from django.contrib import messages


def index(request):
	if "user_id" in request.session:
		return(redirect("/dashboard"))
	return render(request, "Belt_app/login.html")

def register(request):
	results = User.objects.validate(request.POST)
	if not results[0]:
		request.session['first_name'] = request.POST["first_name"]
		request.session['last_name'] = request.POST["last_name"]
		request.session['email'] = request.POST["email"]
		for error_message in results[1]:
			messages.add_message(request, messages.ERROR, error_message)

	return(redirect("/"))

def login(request):
	results = User.objects.log(request.POST)

	if not results[0]:
		for error_message in results[1]:
			messages.add_message(request, messages.ERROR, error_message)
		return(redirect("/"))
	else:
		request.session["user_id"] = results[1].id
		request.session["first_name"] = results[1].first_name
		return(redirect("/dashboard"))

def logout(request):
	request.session.clear()
	return redirect("/")

def dashboard(request):
	if "user_id" not in request.session:
		return(redirect("/"))

	quoteable = Quote.objects.all()
	favorited = User.objects.get(id=request.session["user_id"]).favoritequote.all()

	for f in favorited:
		# refers to variable in for loop
		quoteable = quoteable.exclude(id=f.id)

	allquotes = {
		"quoteable": quoteable,
		"favorited": favorited,
	}
	return render(request, "Belt_app/dashboard.html", allquotes)

def postqoute(request):
	if "user_id" not in request.session:
		return(redirect("/login"))

	results = Quote.objects.qvalid(request.POST)

	if not results[0]:
		for error_message in results[1]:
			messages.add_message(request, messages.ERROR, error_message)

	return(redirect("/dashboard"))

def makefavorite(request, quote_id):
	this_user = User.objects.get(id=request.session["user_id"])
	this_quote = Quote.objects.get(id=quote_id)
	this_quote.favorite.add(this_user)

	return(redirect("/dashboard"))

def removefavorite(request, quote_id):
	this_user = User.objects.get(id=request.session["user_id"])
	this_quote = Quote.objects.get(id=quote_id)
	this_quote.favorite.remove(this_user)

	return(redirect("/dashboard"))

def viewuser(request, user_id):
	if "user_id" not in request.session:
		return(redirect("/"))

	userpageinfo = {
		"userinfo": User.objects.get(id=user_id),
		"quoteinfo": Quote.objects.filter(quotemaker__id=user_id),
	}
	# creates a count and then adds that value to the dictionary, userpageinfo
	count = 0
	for i in userpageinfo["quoteinfo"]:
		count+=1
	userpageinfo["count"] = count

	return render(request, "Belt_app/viewuser.html", userpageinfo)

def deleteQuote(request, quote_id):
	if "user_id" not in request.session:
		return(redirect("/"))
	quote = Quote.objects.get(id=quote_id)
	user = User.objects.get(id=request.session["user_id"])

	if quote.quotemaker == user:
		Quote.objects.get(id=quote_id).delete()

	return redirect("/viewuser/"+request.POST["user_page"]);

