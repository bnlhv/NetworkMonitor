# Q1 - Network Monitor
## _User Manual Guide_

Network Monitor is a cli tool to control network interface monitoring on your computer.
This solution is based on python programming language.
1. For starting the project you'll need both python and docker on your computer (win\unix).
2. Unzip the source code to the path you'd like.
3. To make life easier, I've wrote scripts for both os (using these also at the "start at boot" requirement).
    a. `Unix`: run `./unix-script.sh` in your terminal.
    b. `Windows`: run `win-script.bat` in cmd.
4. Wait to see the server running logs.
5. Integrate the server with cli client. In another terminal run in projects root directory the following command:  
`python client/main.py --help`, you'll see the clients "man page".  
6. Client commands:  
    a. `python client/main.py get_nics`: To get all available nics names.
    b. `python client/main.py check_nic_threshold {NIC_NAME}`: Get a response of NIC rate validation (not too high, not too low).
    c. `python client/main.py change_min_dl_threshold {NEW_THRESHOLD}`: Update the min download threshold value in server.
    d. `python client/main.py change_max_dl_threshold {NEW_THRESHOLD}`: Update the max download threshold value in server.
    e. `python client/main.py change_min_ul_threshold {NEW_THRESHOLD}`: Update the min upload threshold value in server.
    f. `python client/main.py change_max_ul_threshold {NEW_THRESHOLD}`: Update the max upload threshold value in server.
    g. `python client/main.py get_snapshot`: Get pic of line plot of upload and download rates in the last minute, the file would save in plot dorectory.
7. Integrate with the server via api calls through `http://localhost:8000/...` (recommended to use fastapi openapi & swagger integration in  `http://localhost:8000/docs/`)
8. To make this program run on boot, follow these steps:
    a. `Unix` - enter this command to crontab file `@reboot ./path/to/script/unix-script.sh`
    b. `Windows` - Go to Run window (Winkey+R) and run `shell:startup` and a file explorer in the right place would open. Paste the `win-script.bat` file in that directory (don't forget to update file paths inside the .bat file)

## Features
- Get online network interfaces
- Get the current interface rate and know if it's valid
- Change thresholds for last sections validation check
- Know if network interface card is down
- Get plot visualization of NICs preformance

## Key milestones in the project development
- Finding solution for getting NICs live data.
- Finding formula to calculate NICs rate.
- Development of the server and database.
- Development of the client and cli.

## Key requirements in the project
- Getting live data from the os.
- Check NICs threshold validation.
- Log when NIC is down.

## Why I chose this solution
- I chose `python` because that's my day-to-day programming language and I can show my skills this way.
- I chose `FastAPI` framework because **I don't work with it on daily bases and this is an opportunity to learn**
- I chose `MongoDB` because Non-Relational Databases tend scale better than Relational (Horizontal) and because I store each Bandwidth samlpe the data is huge.
- I chose `MongoDB` framework because **I don't work with NoSQL databases on daily bases and this is an opportunity to learn**
- I chose `Docker` container because this makes the tester life easier not downloading mongo service.
- I chose python packse `Fire` for cli tool bause it's an easy and friendly cli wrapper on python scripts.

## Problems I've encountered
- I wanted to create a react app for the frontend but it consumed a lot of my time (I learned for this homework) so my solution was a cli tool.
- I created the server as a docker container which was very helpful for tester that doesn't have python on his host but there are few difficulties with sharing host network data with containers (containers are meant to be isolated from the host), it's posible but only for unix os and not with all the relevant data.  
- After I decided to run the server as a service script there was a difficulty running the client cli from a container and integrating with the host (can be solved with running container with `--network=host` flag but only available in unix) so the solution was to call the functions as the manual now says.  
- When I created the docker containers I've configured a message queue for pub\sub design pattern with `redis` and `redis-rq` which is the implementation of messaging queue and workers for python (I work on daily bases with celery & rabbitmq so I wanted to learn something new). I had difficulties sharing the same DB connection instance between different worker containers because those are different processes my solution as I saw that I need to back down from server in container was to make those tasks as a periodic task inside the framework but coupled and not efficient as it can be.
- Due to time problems I didn't write any tests.  

## How I managed to debug:
1. Pythons `pdb` inside processes
2. I've turned on the `--reload` flag on the server so in every change the server renders.
3. I used swagger docs to integrate with the server.
4. I've tested the specific deterministic functions with `Fire` cli tool.

# Q2 - Pcap Parser
### Answers
1. Protocols and their meaning in .pcap file when browsing to www.example.com
    a. `ICMP` - "Hello" protocol, 3rd layer (network) that sends and recieve packets via IP addresses. `ping` is an implementation of `ICMP`.
    b. `UDP` - Transport layer protocol (4th), known for it's fast and non-reliable connection to destination. This is done because `UDP` doesn't check that data arrived and sends datagrams. Some `UDP` implementations are : `DNS`, `VOIP`, etc.
    c. `TCP` - Transport layer protocol (4th), known for it's reliable manner. each new connections is done with the syn-ack mechanism flow. The destanation makes sure the segment arrived fully. It is used over applications that data transactions are atomic like `SSH`, `FTP`, `HTTP`, `HTTPS`, etc.
    d. `DNS` - Domain Name System, works in Application layer protocol and over UDP/IP. This protocol is used for resolving names for humans to ip addresses to make internet browsing easier. The `DNS` protocol uses classes of servers, there is no one DNS for the world. When a standart `DNS` query isn't answer by local `DNS` then is moves up the chain for higher hierarchy until it gets the right ip address. 
    e. `QUIC` - Designed by google, the protocol is used over more than 50% of connections from Chrome web-browser to google's servers. The main idea of the protocol is multiplexing multiple `UDP` connections and manage them, makes the protocol more efficient of `TCP` for some client-server communications.

## Pcap parser script 
1. You'll need python in your machine.
2. Run `cd path/to/pcap_parser/` & `pip install -r requirements.txt` 
3. Run the script as cli - `python path/to/pcap_parser/main.py {PCAP_FILE_PATH}`
4. _www.ynet.co.il_ - the answer the script has of this is very legit. This site serves in HTTPS protocol and not HTTP, therefore we see TLS encrypted connections from and to the site and not HTTP. In fact, the script is hardcoded with port 80 for the application gateway of HTTP protocol, if we'll change the hardcoded value to 443 (HTTPS) port we'll see the conversation from the client to server (syn-ack syncronize) but without the data (encrypted).

# Q3 - code analysis
```java
void printPairs1(int[] array) {
    for (int i = 0; i < array.length; i++) {
        for (int j = 0; j < array.length; j++) {
            system.out.println(array[i] + ", " + array[j]);
        }
    }
}
```
1. This snippet produces n^2 combinations of the array with itself and print all the couple elements that can exsits.  
2. Time complexity is O(n^2)

# Q4 - code analysis
```java
void printPairs2(int[] arrayA, int[] arrayB) {
    for (int i = 0; i < arrayA.length; i++) {
        for (int j = 0; j < arrayB.length; j++) {
            system.out.println(arrayA[i] + ", " + arrayB[j]);
        }
    }
}
```
1. Time complexity is O(n*m) where each are length of the arrays respectivily.
2. The difference from Q3 is that Q3 in a private case of Q4's snippet where n=m. When they aren't equal the time complexity changes accordingly.
