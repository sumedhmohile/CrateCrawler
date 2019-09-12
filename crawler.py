import sys
import requests
from bs4 import BeautifulSoup
import json

main_list = []


def generate_url_from_crate_name(crate_name):
    if len(crate_name) == 3:
        url_suffix = "3/" + crate_name[0] + "/" + crate_name
    elif len(crate_name) == 2:
        url_suffix = "2/" + crate_name
    elif len(crate_name) == 1:
        url_suffix = "1/" + crate_name
    else:
        url_suffix = crate_name[0:2] + "/" + crate_name[2:4] + "/" + crate_name
    return "https://github.com/rust-lang/crates.io-index/blob/master/" + url_suffix


def get_dependencies_for_crate(crate_name, crate_version):
    global main_list

    url_to_call = generate_url_from_crate_name(crate_name)

    if url_to_call is None or crate_name in main_list:
        return []

    crawl_result = requests.get(url_to_call, stream=True)

    soup = BeautifulSoup(crawl_result.content, 'html5lib')
    result_set = soup.find_all('td', attrs={'class': 'js-file-line'})
    dependencies_list = []

    for result in result_set:
        for tag in result:
            data = json.loads(tag)

            version = data['vers']

            if is_version_match(version, crate_version):
                crate_version = "x"
                dependencies = data['deps']

                for dependency in dependencies:
                    if (dependency['name'], dependency['req']) not in dependencies_list:
                        dependencies_list.append((dependency['name'], dependency['req']))

    res = []
    for dependency in dependencies_list:
        list_for_dependency = get_dependencies_for_crate(dependency[0], dependency[1])
        if len(list_for_dependency) > 0:
            res.extend(list_for_dependency)

    dependencies_list.extend(res)

    for dependency in dependencies_list:
        main_list.append(dependency[0])

    return dependencies_list


def is_version_match(version1, version2):
    version1 = version1.strip("^")
    version2 = version2.strip("^")

    if len(version2) < len(version1):
        version1, version2 = version2, version1

    return version1 == version2[0:len(version1)]


cr_name, cr_version = sys.argv[1], sys.argv[2]
all_dependencies = get_dependencies_for_crate(cr_name, cr_version)

for dependency_entry in all_dependencies:
    print("dependency: " + dependency_entry[0] + " | version: " + dependency_entry[1])
