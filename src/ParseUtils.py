import requests
from bs4 import BeautifulSoup


def get_movies_urls():
    urls = []
    for i in range(1, 11):
        urls.append('http://chakoteya.net/movies/movie' + str(i) + '.html')
    return urls


def get_episode_urls(series):
    list_page_url = ''
    base_url = ''
    if series == 'StarTrek' or series == 'NextGen' or series == 'DS9' or series == 'Enterprise':
        list_page_url = 'http://chakoteya.net/' + series + '/episodes.htm'
        base_url = 'http://chakoteya.net/' + series + '/'
    elif series == 'VOY':
        list_page_url = 'http://chakoteya.net/Voyager/episode_listing.htm'
        base_url = 'http://chakoteya.net/Voyager/'
    # Only season one of Discovery is transcribed
    elif series == 'DIS':
        list_page_url = 'http://chakoteya.net/STDisco17/episodes.html'
        base_url = 'http://chakoteya.net/STDisco17/'
    # Picard and Lower Decks transcripts are not up yet
    elif series == 'PIC':
        list_page_url = 'http://chakoteya.net/StarTrekPIC/episodes.html'
        base_url = 'http://chakoteya.net/StarTrekPIC/'
    elif series == 'LD':
        list_page_url = 'http://chakoteya.net/StarTrekLD/episodes.html'
        base_url = 'http://chakoteya.net/StarTrekLD/'
    # Only TOS and TNG movies are transcribed
    elif series == 'movies':
        return get_movies_urls()

    source = requests.get(list_page_url).content
    soup = BeautifulSoup(source, 'html.parser')
    tds = soup.find_all('td')
    urls = []
    for td in tds:
        link = td.find('a')
        try:
            url = base_url + link['href']
            if url not in urls:
                urls.append(url)
        except KeyError:
            continue
        except TypeError:
            continue
    return urls


def sanitize_list(raw_list):
    sanitized_list = []
    for line in raw_list:
        if line == '\n':
            continue
        else:
            sanitized_list.append(line.replace('\n', '').replace('\r', ' '))
    return sanitized_list


def get_lines(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    raw_list = soup.find_all(text=True)
    sanitized_list = sanitize_list(raw_list)
    return sanitized_list


def get_opening_log(lines):
    scene = {
        'location': 'none',
        'dialog': [],
        'characters': [],
        'action': [],
        'logs': [],
        'misc': []
    }
    for line in lines:
        if 'log' in line:
            scene['logs'].append(line)
    return scene


def parse_scene(scene_location, scene_body):
    scene_dict = {}
    characters_in_scene = []
    scene_actions = []
    dialog_in_scene = []
    voice_overs = []
    misc = []
    for line in scene_body:
        if line[0] == '(':
            scene_actions.append(line.replace('(', '').replace(')', ''))
        else:
            try:
                character, dialog = line.split(':')
                character = character.upper()
                characters_in_scene.append(character)
                dialog_in_scene.append(dialog.strip())
                if character not in scene_dict:
                    scene_dict[character] = []
                scene_dict[character].append(dialog)
            except ValueError:
                if 'log' in line:
                    voice_overs.append(line)
                else:
                    misc.append(line)

    sanitized_character_list = []
    [sanitized_character_list.append(x) for x in characters_in_scene if x not in sanitized_character_list]
    return {
        'location': scene_location.upper(),
        'dialog': scene_dict,
        'characters': sanitized_character_list,
        'action': scene_actions,
        'logs': voice_overs,
        'misc': misc
    }


def get_scene(episode_lines, start_index, length):
    scene_name = episode_lines[start_index].replace('[', '').replace(']', '')
    scene_lines = []
    for i in range(start_index + 1, length):
        line = episode_lines[i]
        if line[0] != '[':
            scene_lines.append(line)
        else:
            return scene_name, scene_lines
    else:
        return scene_name, scene_lines


def parse_episode(episode_lines):
    episode_line_length = len(episode_lines)
    scenes = []
    opening = []
    bracket_found = False

    for index, line in enumerate(episode_lines):
        if 'HTML' in line:
            continue
        elif not bracket_found:
            opening.append(line)
        if line[0] == '[':
            if not bracket_found:
                scenes.append(get_opening_log(opening))
                bracket_found = True
            scene_location, scene_lines = get_scene(episode_lines, index, episode_line_length)
            scenes.append(parse_scene(scene_location, scene_lines))
    return scenes


def get_series_parsed_episodes(series_id):
    episodes = []
    episode_urls = get_episode_urls(series_id)
    for episode in episode_urls:
        page_source = requests.get(episode).content
        episode_lines = get_lines(page_source)
        try:
            prefix, title = episode_lines[1].split(' -')
            title = title.strip()
        except ValueError:
            title = episode_lines[1]
        scenes = parse_episode(episode_lines)
        episodes.append({
            'title': title,
            'scenes': scenes
        })
    return episodes
