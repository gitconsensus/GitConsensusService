from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, send_from_directory
from gitconsensusservice import app


@app.route('/')
def index():
    return redirect('https://www.gitconsensus.com/')
