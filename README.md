![Alt text](hostinguard.png?raw=true "Title")

# HostinGuard
[![Build Status](https://travis-ci.com/mirkochip/hostinguard.svg?branch=master)](https://travis-ci.com/mirkochip/hostinguard)
[![Code Coverage](coverage.svg)](https://travis-ci.com/mirkochip/hostinguard)

## The project
A beautiful technical performance dashboard for your hosted web site based on Python, Django, Elasticsearch and Grafana.

## History
In 2016 I wanted to help a friend of mine having some severe technical issues with his own hosted high traffic web site. 

He experienced a crucial loss of visitors and revenue, so I decided to build for him a technical performance dashboard. Getting beyond the hosting limitations (e.g. permissions regarding installation of software) he was finally able to constantly monitoring the VPS technical performances.

Turning on HostinGuard, after a short while, we discovered slow response times, tons of 50x errors, and very odd workload trends.    

Thanks also to HostinGuard, my friend's web site is now back again on track, being one of the most visited of its sector. 

## Requirements
- python 3.6
- python3-venv

## Initial Setup
- Create a virtual environment: `python -m venv venv`
- Activate the virtual environment: ` source venv/bin/activate`
- Install dependencies: ` pip install -r requirements.txt`
- Run it! `python src/manage.py runserver`

## References
I talked about HostinGuard at the [Linux Day 2018 in Bari](https://ld18bari.gitlab.io/linuxday/) (Italy). Check out [here](https://ld18bari.gitlab.io/linuxday/slides/HostinGuard%20-%20Linux%20Day%202018.pdf) the slides! (Italian only)
