#!/usr/bin/python3

import os
import socket
import requests
import json
import concurrent.futures
import argparse

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def read_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def check_url(url, success_codes, timeout, verify_tls):
    try:
        response = requests.get(url, timeout=timeout, verify=verify_tls)
        status_code = response.status_code
        success = status_code in success_codes
        return {'url': url, 'status_code': status_code, 'success': success}
    except requests.exceptions.RequestException:
        return {'url': url, 'status_code': None, 'success': False}

def main(query):
    parser = argparse.ArgumentParser(description='HTTP Health Check Script')
    parser.add_argument('--report', action='store_true', help='Output full report')
    parser.add_argument('--simple', action='store_true', help='Output simple report')
    args = parser.parse_args()

    config = read_config('config.json')
    urls = config['urls']
    timeout = config['timeout']
    success_codes = config['success_codes']
    verify_tls = config['verify_tls']

    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(check_url, url, success_codes, timeout, verify_tls): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            result = future.result()
            results.append(result)

    total_urls = len(urls)
    total_successful = sum(1 for result in results if result['success'])
    total_unsuccessful = total_urls - total_successful
    health_status = 'Healthy' if total_unsuccessful == 0 else 'Unhealthy'

    output = {
        'urls': total_urls,
        'successful_responses': total_successful,
        'unsuccessful_responses': total_unsuccessful,
        'health_status': health_status,
        'results': results,
        'hostname': socket.gethostname()
    }

    if health_status == "Healthy":
        http_response = '200 OK'
    elif health_status == "Unhealthy":
        http_response = '503 Service Unavailable'

    if args.report or query == "report":
        mime_type = "application/json"
        json_output = json.dumps(output, indent=4)
        return(json_output, http_response, mime_type)
    elif args.simple or query == "simple":
        mime_type = "application/json"
        simple_output = {'health_status': health_status}
        json_output = json.dumps(simple_output, indent=4)
        return(json_output, http_response, mime_type)
    else:
        mime_type = "text/plain"
        return(health_status, http_response, mime_type)

def application(env, start_response):
    query = (env['QUERY_STRING'])
    result = main(query)
    start_response(result[1], [('Content-Type',result[2])])
    return [result[0].encode('utf-8')]

if __name__ == '__main__':
    result = main(None)
    print(result[0])
