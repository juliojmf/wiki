from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.core.exceptions import ValidationError
from . import util
from markdown2 import Markdown
import random

list_entries = [entry.lower() for entry in util.list_entries()]

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def wikipage(request, title):
    try:
        markdowner = Markdown()
        tmplt = markdowner.convert(util.get_entry(title))
        return render(request, "encyclopedia/entries.html", {
            "title": title,
            "tmplt": tmplt
        })
    except TypeError:
        return HttpResponse("<h1>Error 404, page not found!</h1>")


def search(request):
    query = request.GET["q"]
    match_search = [entry for entry in util.list_entries() if query.lower() in entry.lower()]
    if query in list_entries:
        return HttpResponseRedirect(reverse("wikipage", args=[query]))
    else:
        return render(request, "encyclopedia/search_results.html",{
            "match_search": match_search
        })


class CreateNewPage(forms.Form):
    title = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)


class EditPage(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="")


def new_page(request):
    if request.method == "POST":
        form = CreateNewPage(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            if title.lower() in list_entries:
                raise ValidationError("Entry already exists", code="repeated")
            else:
                with open(f"./entries/{title}.md", "w") as file:
                    file.write(f"# {title} \n\n {body}")
            return HttpResponseRedirect(reverse("wikipage", args=[title]))
        else:
            return render(request, "encyclopedia/new_page.html", {
                "form": form
            })
    return render(request, "encyclopedia/new_page.html", {
        "form": CreateNewPage()
    })


def edit_page(request, title):
    if request.method == "POST":
        form = EditPage(request.POST)
        if form.is_valid():
            text = form.cleaned_data['content']
            with open(f"./entries/{title}.md", "w") as file:
                file.write(text)
            return HttpResponseRedirect(reverse("wikipage", args=[title]))
        else:
            return render(request, "encyclopedia/new_page.html", {
                "form": form
            })
    with open(f"./entries/{title}.md", "r") as file:
        content = file.read()
    return render(request, "encyclopedia/edit_page.html", {
        "form": EditPage(initial={"content":content}),
        "title": title
    })


def random_page(request):
    return HttpResponseRedirect(reverse("wikipage", args=[random.choice(list_entries)]))
