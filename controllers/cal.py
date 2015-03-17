# -*- coding: UTF-8 -*-

# Calendar controller
class Controller:

    def __init__(self,master):
        self.master = master

    def give_404(self):
        return self.master.run_controller('404')

    def make_calendar(self,year,month=0):
        self.master.status = 200
        self.master.content_type = 'text/plain; charset=UTF-8'
        import calendar
        cal = calendar.LocaleTextCalendar(locale=str(self.master.locale))
        if month > 0:
            content = cal.formatmonth(year,month).decode('UTF8')
        else:
            content = cal.formatyear(year).decode('UTF8')
        self.master.template_vars.update(content=content)

    def run(self):
        year = 0
        month = 0
        if self.master.subrequest:
            dateparts = self.master.subrequest.split('/')
            # accept only year/(month)?
            if len(dateparts) < 3:  
                # only numeric years
                if dateparts[0].isdigit(): 
                    year = int(dateparts[0])
                    # only years in allowed range
                    if year < 1 or year > 9998: 
                        year = 0
                    # optionally accepth month
                    elif len(dateparts) == 2:  
                        # numeric month
                        if dateparts[1].isdigit(): 
                            month = int(dateparts[1])
                            # only months in allowed range
                            if month < 1 or month > 12:  
                                year = 0
                        else:
                            year = 0
            if year > 0:
                self.make_calendar(year,month)
            else:
                self.give_404()
        else:
            # fallback calendar: current year
            import datetime
            self.make_calendar(datetime.datetime.utcnow().year)
