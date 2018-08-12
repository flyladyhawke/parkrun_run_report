from bs4 import BeautifulSoup
from re import compile
from itertools import zip_longest
from jinja2 import Environment, FileSystemLoader


class RunReportUtils:

    @staticmethod
    def get_sections(seq, num):
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + num)])
            last += num

        return out

    @staticmethod
    def chunks(seq, chunk_size):
        """Yield successive chunkSize-sized chunks from list."""
        for i in range(0, len(seq), chunk_size):
            yield seq[i:i + chunk_size]

    @staticmethod
    def reverse_find(haystack, needle, n):
        pos = len(haystack)
        for i in range(0, n):
            pos = haystack.rfind(needle, 0, pos)
        return pos


class RunReport(object):
    parkrun_name = ''
    parkrun_event_number = ''
    options = {
        'template_name': 'base',
        'runner_limit': 7,
        'volunteer_limit': 2,
        'pb_limit': 2,
        'number_event_urls': 8
    }

    template_loader = False
    template_env = False
    
    results_system_text = ''
    current_event_volunteers = []
    current_event_runners = {}

    event_result_count = []
    runners = {}
    volunteers = {}
    photos = []
    toc = []

    content_text = {}
    
    VOLUNTEER_START_TEXT = 'We are very grateful to the volunteers who made this event happen:'
    PB_TEXT = 'New PB!'
    RESULT_SYSTEM_START_TEXT = 'This week'

    def __init__(self, name, event_number):
        self.parkrun_name = name
        self.parkrun_event_number = event_number

        self.template_loader = FileSystemLoader(searchpath="templates/")
        self.template_env = Environment(loader=self.template_loader)
        self.template_env.trim_blocks = True
        self.template_env.lstrip_blocks = True
  
        # make sure these are reset each time you call the init
        self.runners = {}
        self.volunteers = {}

    def set_results_system(self, text):
        text = text.strip()
        if text == '':
            return
        if len(text) > 3000:
            print("Result System Text is limited to 3000 characters\nAre you sure you copied from the results system?")
            return
        self.results_system_text = text

    def reset_event_result(self):
        self.current_event_volunteers = []
        self.current_event_runners = {}
        self.runners = {}
        self.volunteers = {}

    def parse_event_result(self, is_current=False, text=''):
        text = text.strip()
        if text == '':
            return
        if len(text) > 500000:
            print("Event Text is limited to 500,000 characters")
            return
        if is_current:
            self.set_current_event(text)
        self.parse_runners(text)
        self.parse_volunteers(text)

    def parse_optional_text(self, text_type, text):
        text = text.strip()
        if text == '':
            return
        if len(text) > 3000:
            print("Optional Text is limited to 3000 characters")
            return
        self.content_text[text_type] = text.format(self.parkrun_name)

    def set_current_event(self, text):
        text = text.strip()
        if text == '':
            return
        # set currentEventRunners and currentEventVolunteers 
        self.set_current_event_runners(text)
        self.set_current_event_volunteers(text)
            
    def parse_current_event(self, text, parse_type):
        soup = BeautifulSoup(text, 'html.parser')
        rows = []
        if parse_type == 'runners':
            # get every row from the result table
            rows = soup.find(id="results").find("tbody").find_all("tr")
        elif parse_type == 'volunteers':
            # <p class="paddedb">
            # We are very grateful to the volunteers who made this event happen:
            # </p>  
            start = soup.p.find(text=compile(self.VOLUNTEER_START_TEXT))
            pos = start.find(':')
            sub = start[pos+1:]
            rows = sub.split(', ')          
        return rows    
            
    def set_current_event_runners(self, text):
        self.current_event_runners = {}
        rows = self.parse_current_event(text, 'runners')
        for row in rows:
            details = self.get_runner_details(row.find_all("td"))
            if details:
                self.current_event_runners[details['id']] = {
                    "name": details['name'],
                    "time": details['time'],
                    "age_group": details['age_group']
                }
                
    def set_current_event_volunteers(self, text):
        self.current_event_volunteers = []
        names = self.parse_current_event(text, 'volunteers')
        for n in names:
            self.current_event_volunteers.append(n)
           
    def get_runner_details(self, cells):
        # <tr>
        # <td class="pos">2</td>
        # <td><a href="athletehistory?athleteNumber=111111" target="_top">Firstname LASTNAME</a></td>
        # <td>18:14</td>
        # <td><a href="../agecategorytable/?ageCat=SM30-34">SM30-34</a></td>
        # <td>71.12 %</td>
        # <td>M</td>
        # <td>2</td>
        # <td><a href="../clubhistory?clubNum=1187"/></td>
        # <td>New PB!</td>
        # <td>2</td>
        # <td style="min-width:72px"/>
        # </tr>
        cell = cells[1]
        name = cell.get_text()        
        if name != 'Unknown':
            href = cell.a["href"]
            # format of href="athletehistory?athleteNumber=208507"
            pos = href.find('=')
            athlete_id = href[pos+1:]
            
            time = cells[2].get_text()
            age_group = cells[3].get_text()
            position = cells[0].get_text()
            pb = 0
            if cells[8].get_text() == self.PB_TEXT:
                pb = 1

            return {
                "id": athlete_id,
                "name": name,
                "time": time,
                "pb": pb,
                "age_group": age_group,
                "position": position
            }
        else:
            return False  
        
    def parse_runners(self, text):
        text = text.strip()
        if text == '':
            return	
        rows = self.parse_current_event(text, 'runners')
        event_count = 0
        for row in rows:
            cells = row.find_all("td")
            details = self.get_runner_details(cells)
            if details:
                event_count = event_count + 1
                pb_count = 0
                if details['id'] in self.runners:
                    count = self.runners[details['id']]['count'] + 1
                    if details['pb'] == 1:
                        pb_count = self.runners[details['id']]['pb_count'] + 1
                    else:
                        pb_count = self.runners[details['id']]['pb_count']
                else:
                    count = 1
                    if details['pb'] == 1:
                        pb_count = 1

                self.runners[details['id']] = {"name": details['name'], "pb_count": pb_count, "count": count}
        self.event_result_count.append(event_count)
        # display number of runners as you parse each event result
        # this is to indicate to the user that something is happening
        # and as a visual guide that they can see the the totals, and double check data if duplicate numbers
        # i.e. they didn't accidentally copy and paste from the same event twice
        print('Event with '+str(event_count)+' known runners added')
        
    def parse_volunteers(self, text):
        text = text.strip()
        if text == '':
            return

        names = self.parse_current_event(text, 'volunteers')
        for n in names:
            if n in self.volunteers:
                count = self.volunteers[n] + 1
            else:
                count = 1
            self.volunteers[n] = count

    def reset_photos(self):
        self.photos = []
            
    def add_photo(self, size, photo_type, title='', text=''):
        text = text.strip()
        if text == '':
            return
        if len(text) > 300:
            print("Photo Text is limited to 300 characters")
            return
        start_pos = text.find('[img]') + len('[img]')
        end_pos = text.find('.jpg') + len('.jpg')
        flickr_link = text[start_pos:end_pos]
        
        self.photos.append({'link': flickr_link, 'size': size, 'type': photo_type, 'title': title})
     
    def get_photo_links(self, photo_type):
        photos = []
        # width of 620 works best of the parkrun wordpress page
        picture_width = 620
        for p in self.photos:
            if p['type'] == photo_type:
                dims = p['size']
                curr_width = int(dims[0])
                curr_height = int(dims[1])
                # resize to a standard width of picture_width if picture is landscape
                if curr_width >= curr_height:
                    dims[0] = picture_width
                    dims[1] = (picture_width * curr_height) // curr_width
                # resize to a width that allows 2 pictures on a line if picture are portrait
                elif curr_height > curr_width:
                    # get two pictures on one row
                    dims[0] = picture_width // 2 - 5
                    dims[1] = ((picture_width / 2 - 5) * curr_height) // curr_width
                photos.append({
                    'link': p['link'],
                    'alt': p['type'],
                    'width': dims[0],
                    'height': dims[1],
                    'title': p['title']
                })
        return photos
        
    def get_aesthetic_times(self):
        times_list = []

        for key, data in self.current_event_runners.items():
            time = data['time']
            # end in :00 or start = end like 21:21
            if time[-2:] == '00' or time[-2:] == time[0:2]:
                times_list.append(str(time) + ' - ' + data['name'])
            # e.g. 22:33    
            elif time[0] == time[1] and time[3] == time[4]:
                times_list.append(str(time) + ' - ' + data['name'])
            # e.g. 21:12               
            elif time[0] == time[4] and time[1] == time[2]:
                times_list.append(str(time) + ' - ' + data['name'])

        return times_list

    def calc_age_groups(self):
        runners = self.current_event_runners
        age_group = {}
        # results are sorted by position number, so first found for each age group is the fastest
        for l, v in runners.items():
            age = v['age_group']
            age_number = age[2:]
            details = {'name': v['name'], 'time': v['time']}
            if age[0:2] == 'SM' or age[0:2] == 'VM':
                if age_number not in age_group:
                    age_group[age_number] = {'man': details, 'woman': {'name': '', 'time': ''}}
                elif age_group[age_number]['man']['name'] == '':
                    age_group[age_number]['man'] = details
            elif age[0:2] == 'SW' or age[0:2] == 'VW':
                if age_number not in age_group:
                    age_group[age_number] = {'man': {'name': '', 'time': ''}, 'woman': details}
                elif age_group[age_number]['woman']['name'] == '':
                    age_group[age_number]['woman'] = details
        sorted_age = sorted(age_group.items(), key=lambda x: x[0])
        return sorted_age
        
    def get_age_group_finisher_summary(self):
        headers = [
            {'width': 20, 'text': 'Age Group', 'colspan': 1},
            {'width': 40, 'text': 'Men', 'colspan': 2},
            {'width': 40, 'text': 'Women', 'colspan': 2}
        ]
        summary_data = self.calc_age_groups()
        data = []
        for l, v in summary_data:
            data.append([l, v['man']['name'], v['man']['time'], v['woman']['name'], v['woman']['time']])

        return {'headers': headers, 'data': data}
        
    def get_regular_summary(self, runner_limit, volunteer_limit):
        events = len(self.event_result_count)
        headers = [
            {'width': 50, 'colspan': 1, 'type': 'Runners', 'limit': runner_limit, 'events': events},
            {'width': 50, 'colspan': 1, 'type': 'Volunteers', 'limit': volunteer_limit, 'events': events}
        ]
        # get the sorted name column for all runners with count above runner_limit
        regular_runners = [v['name'] for k, v in self.runners.items() if v['count'] >= runner_limit]
        runners_names = sorted(regular_runners)

        # get the sorted name column for all volunteers with count above volunteer_limit
        regular_volunteer = [k for k, v in self.volunteers.items() if v >= volunteer_limit]
        volunteer_names = sorted(regular_volunteer)
        # display as two columns, one for runners, one for volunteers, and they will probably be different lengths
        # so need to transpose the data
        combined = [runners_names, volunteer_names]
        data = list(zip_longest(*combined, fillvalue=''))

        return {'headers': headers, 'data': data}

    def get_pb_summary(self, pb_limit=2, data_columns=2):
        events = len(self.event_result_count)
        headers = [{'width': 100, 'colspan': data_columns, 'type': 'PBs', 'limit': pb_limit, 'events': events}]
        # get the sorted name column for all runners with pb_count above pb_limit
        summary_data = sorted([v['name'] for k, v in self.runners.items() if v['pb_count'] >= pb_limit])
        if data_columns == 1:
            data = summary_data
        else:
            # create list of data_columns size lists so the data can be multiple columns
            data = list(RunReportUtils.chunks(summary_data, data_columns))

        return {'headers': headers, 'data': data}


class RunReportWeek(RunReport):
    
    parkrun_week = 1
    run_report_html = ''
    sections = []
    
    def __init__(self, name, event_number):
        RunReport.__init__(self, name, event_number)        
        
    def print_urls(self, week, number_event_urls):
        links = []
        self.parkrun_week = week
        event_number = str(self.parkrun_event_number)       
        links.append('tag: ' + self.parkrun_name + '_parkrun_' + event_number)
        links.append('tag: ' + self.parkrun_name)
        links.append('tag: parkrun')
        links.append('https://www.flickr.com/groups_pool_add.gne?path=' + self.parkrun_name + '-parkrun')
        links.append('https://www.flickr.com/groups/' + self.parkrun_name + '-parkrun/')
        links.append('http://www.parkrun.com.au/'
                     + self.parkrun_name + '/results/weeklyresults/?runSeqNumber='
                     + event_number)
        
        if week == 2 or week == 3:
            for i in range(1, number_event_urls):
                event_number = str(self.parkrun_event_number - i)
                links.append('http://www.parkrun.com.au/'
                             + self.parkrun_name + '/results/weeklyresults/?runSeqNumber='
                             + event_number)

        return links

    def create_week(self, week=False, options=False):
        self.sections = []
        self.toc = []

        self.add_summary_section()
        # self.add_upcoming_section()
        self.add_volunteer_section()
        self.add_milestone_section()
        
        # allow override of week and options since week and options in class init are only used for link creation.
        if week is not False:
            self.parkrun_week = week
            
        # merge options
        if options is not False:
            self.options = {**self.options, **options}
        
        if self.parkrun_week == 1:
            self.add_age_group_section()
        elif self.parkrun_week == 2:
            self.add_regular_section(self.options['runner_limit'], self.options['volunteer_limit'])
        elif self.parkrun_week == 3:
            self.add_week_pb_section(self.options['pb_limit'])
        elif self.parkrun_week == 4:
            self.add_community_section()
            
        self.add_times_section()
        self.add_photo_section()

        args = {'sections': self.sections, 'toc': self.toc}
        template = self.template_env.get_template(self.options['template_name'] + ".html")
    
        return template.render(args)

    def add_summary_section(self):
        text = self.results_system_text
        # find string position of third last .
        needle = '.'
        pos = RunReportUtils.reverse_find(text, needle, 3)

        section = {
            'heading': 'Summary',
            'anchor': 'summary',
            'content': {
                'start': '',
                'list': [
                    text[text.find(self.RESULT_SYSTEM_START_TEXT):text.find('.') + 1],
                    text[pos + 1:].strip()
                ],
                'end': self.content_text['summary'],
            },
            'separator': True
        }

        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
    
    def add_upcoming_section(self):
        # Only add section if there is upcoming text
        content = self.content_text['upcoming']
        if content == '':
            return
        section = {
            'heading': 'Upcoming',
            'anchor': 'upcoming',
            'content': self.content_text['upcoming'],
            'separator': True
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})

    def add_milestone_section(self):
        # Only add if there are any milestones
        photo_links = self.get_photo_links('milestone')
        if len(photo_links) == 0:
            return

        section = {
            'heading': 'Milestones',
            'anchor': 'milestone',
            'photos': photo_links,
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
        
    def add_volunteer_section(self):
        section = {
            'heading': 'Volunteers',
            'anchor': 'volunteers',
            'content': {
                'start': self.content_text['volunteer'],
                'list': self.current_event_volunteers,
            },
            'separator': True,
            'photos': self.get_photo_links('volunteer')
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
    
    def add_age_group_section(self):
        section = {
            'heading': 'Age Group First Finishers',
            'anchor': 'age_group',
            'summary_data': self.get_age_group_finisher_summary()
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
        
    def add_regular_section(self, runner_limit=7, volunteer_limit=2):
        section = {
            'heading': 'Regular Runners / Volunteers',
            'anchor': 'regular',
            'summary_data': self.get_regular_summary(runner_limit, volunteer_limit)
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
        
    def add_week_pb_section(self, pb_limit=2):
        section = {
            'heading': 'Regular PBs',
            'anchor': 'pbs',
            'summary_data': self.get_pb_summary(pb_limit)
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
            
    def add_community_section(self):
        # TODO work out what to do here
        content = ''
        section = {
            'heading': 'Having Fun',
            'anchor': 'fun',
            'content': content
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
        
    def add_times_section(self):
        section = {
            'heading': 'Aesthetically pleasing times',
            'anchor': 'times',
            'content': {
                'list': self.get_aesthetic_times(),
            },
            'separator': True
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
            
    def add_photo_section(self):
        section = {
            'heading': 'Photos',
            'anchor': 'photos',
            'photos': self.get_photo_links('photo')
        }
        self.sections.append(section)
        self.toc.append({'heading': section['heading'], 'anchor': section['anchor']})
