                         
<br/>
<div align="center">
<a href="https://youtu.be/5RQiOE0xpWI">
<img src="https://github.com/user-attachments/assets/8ed70f78-0e5a-4515-a386-1e29182752af" alt="Logo" width="700" height="400">
</a>
<h3 align="center">Stream and Upload Video Powered by Proven Celery Pipeline, S3, Gcore CDN and PlayReady DRM<a href="https://www.youtube.com/watch?v=5RQiOE0xpWI"  target="_"><strong> Watch in Action</strong></a></h3>
<p align="center">
CuteTube is a Video On Demand (VoD) Platform Just Like  <a href="https://www.youtube.com/watch?v=5RQiOE0xpWI" target="_"><strong>YouTube</strong></a>
  <br/>
  <p style="text-align: center;">
  The microservices version of CuteTube is Movio. Check it <a href="https://github.com/Mahboob-A/movio/" target="_blank"><strong>here »</strong></a>
</p>
<br/>
<br/>
<a href="https://imehboob.medium.com/my-experience-building-a-leetcode-like-online-judge-and-how-you-can-build-one-7e05e031455d"  target="_"><strong>Read the blog »</strong></a>
<br/>
<br/>
</p>
</div>
<h3 align="center">General Information | CuteTube Monolith Version</h3>

**CuteTube** is a _**High Performance**_ video streaming platform just like <a href="https://www.youtube.com/">_YouTube_</a>. A viewer can signup in _CuteTube_ and watch their favorite videos as well as upload their video for others to watch. 

**CuteTube** is primarily tries to mimic the core backend of any established _VoD_ platforms. The backend of **CuteTube**  is built on `Django`.

The _CuteTube_ platform is backed by the following core technologies - 

    a. Django - The Backend
    b. Proven Celery Pipeline - For Asynchronous Video Processing  
    c. AWS S3 - Store the DASH Segments
    d. FFmpeg - Transcode, Segment Videos in MPEG-DASH with Adaptive Bitrate Streaming Technology
    e. Gcore CDN - Distribute the Content Globally with Low Latency
    g. Shaka Packager - Segment and Encrypt the Video with AES 128-bit Key
    h. PlayReady DRM (Test Server) - Video is Protected with Digital Rights Management by PlayReady Test Licence Server  
 

#### *NOTE* 

**A. Architectures of `CuteTube` | `Monolith` and `Microservices`**

> The current implementation you are now reading is built in `Monolith` architecture. 
> 
>> There is another version of  `CuteTube` as `Microserivices` where I have separated services based on concern. The microservices version of `CuteTube` is more `robust` and `scalable` solution with wider range of technologies implemented. 
> 
>>
>>> Please see the `CuteTube` microservices version here - <a href="https://github.com/Mahboob-A/algocode" target="_">CuteTube Microservices</a>

**B. Versioning of CuteTube**

> The _CuteTube_ project has 4 versions. Versioning is simply the different types of implementation of _CuteTube_. Hence, each version (`see in core_apps.stream_v*)` is built differently incorporating basic to advanced technologies. The technology and the range of technology adoption increases as the version increases. 

>> Version 01 => 
>
>
>>> The basic implementation of VoD kind streaming where the backend itself takes a video and returns the video as chunk to the viewer. 
> 
> 
>> Version 02 =>
>
>
>>> The second version is involved with `ffmpeg` in _CuteTube_. The video is `segmented` and the backend serves the `.mpd` file and the `segments` to the user. 
> 
> 
>> Version 03 => 
>
>
>>> The third version is a robust and well tested solution for a `VoD` backend. All the necessary `APIs` in this version are fully automated. `Celery Pipeline`, `S3 Bucket Storage`, `Gcore CDN` for global distribution is implemented in this version. 
> 
> 
>> Version 04 => 
>
>
>>> In the version four, everything that is available in `version 03` is available. But the addition is that `DRM` (Digital Rights Management) is implemented in this version with `Microsoft's PlayReady DRM service`. A DRM helps to `encrypt` the video segments and the client is required to obtain a licence from the `DRM Licence Server` in order to decrypt the video segment to watch. `Shaka Packager` has been used for segmentation purpose in this version of _CuteTube_.  However, version 04 is still under development as the `free Microsoft PlayReady test DRM licence server` does not work as expected all the time and as `it is nearly impossible to get free/trial DRM servers for individual other than PlayReady test DRM licence server`.   
> 
>>>> Additional Note => 
>
>>>>> `CuteTube` is fully `dockerized` solution. 
>
>

**C. Rate Limit Alert**

>> Note that the project is not deployed as the celery pipeline takes too much of resources and a free server can't handle it!! 

> The API endpoint to for stream and upload video in the _CuteTube_ platform is Rate Limited. 
>> ```http 
>>     GET https://cutetube.algocode.site/api/v3/vod/metadata/stream/<str:video_id>/
>> ``` 
>> Fetch Video Metadata to stream video API is rate limited to `1 requests per 20 seconds`. 
> 
>> ```http 
>>     POST https://cutetube.algocode.site/api/v3/vod/initiate-task/upload/
>> ```
> 
>> Upload video to CuteTube API is rate limited to `1 request per 20 minutes` 
>
>
>> You can learn more on API Documentation in the `API Guideline - CuteTube APIs` section.

**D. Containerized Solution**

> The project is fully containerized using docker. A `make docker-up` would run the full system locally provided the `.envs`. 

**E. Documentation**

> Please visit the documentation page `localhost:8080/doc/` for more information related to API documentation. 
> 
>> **PS - Read `Deployment` section to learn why `localhost`**.
> 
<details>
<summary><h3 align="center">Deployment</h3></summary>

#### Deployment Information 

Initially I planned to deploy <a href="https://github.com/Mahboob-A/CuteTube/">CuteTube Backend</a>  on `AWS EC2` in Ubuntu 22.04 server. I have a free `AWS` server but it is impossible to deploy the project in real server as the `Celery Pipeline` needs too much computing power that a `free AWS server` can not provide. The Celery Pipeline itself need at least `3 GB` of `RAM` to continue processing video, where as a `free AWS server` only provides an EC2 instance with `1 GB` of `RAM`  only!

However, I have already attached a detailed video in the `Watch In Action` section how `CuteTube` works in the background. 

</details>

<details>
<summary><h3 align="center">Features</h3></summary>

#### Features of CuteTube


##### Small Note

> As of today I have built the backend platform, and there's no frontend for the project. I am fully focusing on the advanced backend engineering, hence, if you want to contribute or want to build a frontend for the project, please do not hesitate to email me here: 
> [![Email Me](https://img.shields.io/badge/mahboob-black?style=flat&logo=gmail)](mailto:connect.mahboobalam@gmail.com?subject=Hello)
<br/><br/>


##### A. Authentication 

* The authentication system of CuteTube is built from scratch. No `3rd party` packages has been used. 


##### B. Stream 

* Users can request to watch video with `video_id`. 

* The backend service returns the metadata of the video and the dash player plays the video based on the `OS` of the client. 

* The video is served from `Gcore CDN` and `AWS S3` as the origin of the CDN. 

* The CDN is configured with a custom domain `cdn.algocode.site` to serve `segments to the client`. 

* The video segments are available for `mp4` and `mov` container. 



##### C. Upload

* Any authenticated user can upload video to `CuteTube` platform to let watch other users. 

* The video processing is overloaded to a celery pipeline for asynchronous processing, and the user gets an immediate response with process metadata.

* To learn more on the workflow, please take a look at `CuteTube - Architecture and Workflow` Section. 


</details>
<details>
<summary><h3 align="center">Watch In Action</h3></summary>


#### `CuteTube` Monolith  In Action 

- Watch on YouTube

##### Timeline: 

1. Introduction: 00:00 

2. HLD of CuteTube: 09:00  

3. Upload Video to CuteTube: 24:30 

4. Work Distribution on Celery Pipeline: 37:00 

5. S3 Storage of DASH Segments: 46:00 

6. DASH Player: 48:00 

7. Watch the Uploaded Video: 50:00 

8. Rate Limit: 52:15 

9. Flower for Celery Monitoring: 54:15 

<a href="https://www.youtube.com/watch?v=5RQiOE0xpWI" target="_blank">
  <img src="https://img.youtube.com/vi/5RQiOE0xpWI/0.jpg" alt="Watch the video">
</a>

<br>

</details>
<details>
<summary><h3 align="center">Architecture and Workflow  | HLD </h3></summary>


#### Architecture of CuteTube (Monolith Version) 


![image](https://github.com/user-attachments/assets/54ba352f-8a1e-41fd-b515-4b647ea6cebd)



#### Workflow of CuteTube (Monolith Version) 


**A. Authentication**


- The user can `stream i.e. watch` video in `CuteTube` without being authenticated. 

- The user needs to be authenticated to `upload` video in `CuteTube`.  

**B. Stream Video**

- No authentication is needed to watch video in `CuteTube`. 

- User requests with `video_id` to fetch the video metadata. 

- The video metadata is returned to the user 

- The `DASH Segments` type are decided based on `OS` of the client. If the OS is `Windows`, the `MP4` `DASH segments` are played, and for `MacOS` and `Linux`, `MOV` `DASH Segments` are played. 

- The video is played with `ABR` (Adaptive Bitrate Technology). The `DASH player` automatically `upgrades` or `downgrades` to the appropriate bitrate based on the `network condition` of the client. 

- The `ABR` supports `360`, `480`, `720` and `1080` pixels at `800`, `1200`, `2400` and `4800` Kbps respectively. 

- The `Dash segments` are served through `Gcore CDN` and `S3` as the upstream of the CDN. 

- The CDN domain is `cdn.alogcode.site`. 

**C. Upload Video**

- Authentication is needed to `upload` video to `CuteTube`. 

- The user sends the video file and the video metadata such as video name, description etc. through an API. 

- The backend service `saves the video locally`, `initiates a celery pipeline` and `immediately` responses to the client with `process` and `video_id`. 

- The `celery pipeline` does the following when initiated :- 

    - Tracks the original video format i.e. `mov` or `mp4`. `CuteTube` currently processes video with `mov` and `mp4`.  
    
    - Transcodes the video to `mov` container if the original video is in `mp4` container and `vice-versa`. 

    - Creates a few celery `group`, `chord` and `callbacks`, to further process the both videos: Multiple `Celery` processes and tasks are responsible for below workflow : - 

        - The videos are segments with `ABR` technology. 
    
        - The `segments` are prepared in  `group of batches` to `initiate upload in S3`.

        - The `segmet batches` are uploaded to `S3` processing the batches. 

        - The local files are deleted from the local storage and update metadata if needed as `callback`. 

    - The `failed tasks` are `retried` with `exponential backoff` method not to overwhelm the server. 

 - However, the `Microservices` version of `CuteTube` triggers `message queue` events for `producer` at this stage to update the state of the process and to send `notification` or `email` to the user as a token of completion of the video upload process. 

- Please see the <a href="https://github.com/Mahboob-A/algocode-auth" target="_">`Microservices Version` of `CuteTube` </a> to learn more.  

</details>
<details>
  <summary><h3 align="center">API Guideline - Registration in CuteTube</h3></summary>


###  Registration in the CuteTube

>
> Why `localhost`? You probably already know the reason from the **`Deployment`** section!
>


```http
    POST https://localhost:8080/api/v3/auth/signup/
```

| Parameter | Type     |        Description                |
| :-------- | :------- | :------------------------- |
| `username`    | `string` | **Required** Your username for the account.  |
| `email`    | `string` | **Required** Your valid email address.|
| `password`   | `string` | **Required** Your password. | 
| `password2` | `string` |  **Required** Confirm your password. | 
| `first_name` | `string` | **Required**  Your first name. | 
| `last_name` | `string` | **Required** Your last name. | 


<br/>


###  Login in CuteTube

```http
    POST https://localhost:8080/api/v3/auth/login/
```

| Parameter | Type     |        Description                |
| :-------- | :------- | :------------------------- |
| `credential`    | `string` | **Required** Your registered email address or your username.|
| `password`   | `string` | **Required** Your password. | 


<br>

</details><details>
  <summary><h3 align="center">API Guideline - Stream Video on CuteTube</h3></summary>


###  Stream Video on CuteTube

>
> Why `localhost`? You probably already know the reason from the **`Deployment`** section!
>

```http
    GET https://localhost:8080/api/v3/vod/metadata/stream/<video_id>/
```

| Parameter | Type     |        Description                |
| :-------- | :------- | :------------------------- |
| `video_id`    | `string` | **Required** Video ID of the video user wants to stream.  |


<br/>


</details><details>
  <summary><h3 align="center">API Guideline - Upload Video on CuteTube</h3></summary>


###  Upload Video on CuteTube

>
> Why `localhost`? You probably already know the reason from the **`Deployment`** section!
>

```http
    POST https://localhost:8080/api/v3/vod/initiate-task/upload/
```

| Parameter | Type     |        Description                |
| :-------- | :------- | :------------------------- |
| `title`    | `string` | **Required** The title of the Video. |
| `description`    | `string` | **Required** A description of the video.|
| `duration`   | `string` | **Required** Duration of the video in `HH:MM:SS` format. | 
| `video` | `file` |  **Required** A video file either in `.mov` or in `.mp4` format. | 

<br/>



</details><details>
  <summary><h3 align="center">Contributing and Run Locally </h3></summary>

#### Contribution and Development

If you want to contribute or you want to run locally, then you can `fork` the `development` branch on each service mentioned in the `CuteTube` Platform. 

Please follow the `.envs-examples` to know the `env-variables` you would need to run the project locally. 

All the services are `dockerized project`. You just need to `cd src`, create  `virtual environment`, activate it, and 
run `make docker-up` and That's it! 

> PS: `make` will only work if you're using a `linux` or `MacOS` machine and subject to install `makefile` in your system. 
>> Otherwise, you may need to copy the command from the `Makefile` and run the commands. 
> 

This will run the project for you. 

Please follow the service that you want to contribute or run locally to get detailed guideline on local development. 

</details>
<details>
  <summary><h3 align="center">Lessons Learnt and Challenges</h3></summary>

#### The Backstage  

The project itself was a challenge for me! 

Once one of my mentors told me 

> Do the hard things while you are learning, so that the implementation becomes easier for you. 

I completely agree with this statement. I enjoy dealing with complex stuff, and `bugs` give me the `kick` I enjoy! 

Well, enough praise of myself. 

And I am writing this `Readme` today  that I have completed the project, and `somehow` I have made it! That's my motivation. 

I know something is not simple as it sounds, but I know, `somehow I would manage it!` 

#### Challenges 

* The initial challenge was the design. Designing a  complex project like `Video On Demand` in `microservices` to build from `scratch` was not easy as it sounds. 

 * The communication between microservices were fun discovery. I was searching for optimal solution and I learnt `RabbitMQ` for this cause, and I ended up writing a nice blog on `RabbitMQ 101`. Read <a href="https://imehboob.medium.com/message-queue-101-your-ultimate-guide-to-understand-message-queue-b2256961ab01">RabbitMQ 101 Here</a>. The Algocode platform is using an RabbitMQ instance from CloudAMQP platform. 

* I had to re-learn almost everything related to streaming industry. I have to read intense amount of research on `ffmpeg`. I knew nothing about `transcoding`, `segmentation`, `Adaptive Bitrate Streaming`, `DASH`, `HLS`, `Celery Pipeline` but building `CuteTube` taught me a lot on these technologies. 
    

    * However, do you know I have also built a  **`low latency live video streaming platform just like`** <a href="https://www.twitch.tv/" target="_blank">**`Twitch`**</a> named as <a href="https://prostream-gamma.vercel.app/" target="_blank">**`ProStream`**</a>? Please checkout  <a href="https://prostream-gamma.vercel.app/" target="_blank">ProStream here</a>. You'd love to interact with the project, I promise!

<br>

* The most difficult domain was to build the `Celery Pipeline` as it is the core structure for asynchronous processing. I have spent countless sleepless nights just to align the `Celery Pipeline` is well suited and well tested for various use-cases. 

* The `microservices` version of CuteTube was more complex, I had to learn more about `message queue event management` to properly `Acknowledge` tasks based on `factors` deciding whether the `child or related task` was fullfiled or not.   

#### Learnings

* I have gained practical experience with `RabbitMQ` building this project. 

* I have gained deep knowledge on `docker`, `docker volumes`, `docker networking`, `Lunux internals` and many more.

* As the project is heavily dealing with files, I have gained valuable experience with `file handling` with `python`. 

* As I have built the project from `research`, `design`, `dev`, `production` to `deployment`, I have gained invaluable knowledge on design, development, production and deploy the project in `cloud services` like `AWS` or `Azure`. 

* As the project also built in `microservises architecture`, I have gained practical knowledge on `communication`, `networking`,  between all other services; experience with cloud providers such a `AWS`, `Azure`  and onverall `dev to production` of a `SDLC`. 

* As I have built the project in both - `monolith` and `microservices` architecture, I have gained `practical experience`, `advantages`, `disadvantages` on certain parameters for a project on both architectures. I can make more critical judgement on system design how a certain service would behave on `monolith` and `microservices` to maximize the `SDLC` process. 

</details>
<br/>

<a href="https://www.linux.org/" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="Linux" height="40" width="40" />
</a>
<a href="https://postman.com" target="blank">
<img align="center" src="https://www.vectorlogo.zone/logos/getpostman/getpostman-icon.svg" alt="Postman" height="40" width="40" />
</a>
<a href="https://www.w3schools.com/cpp/" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/cplusplus/cplusplus-original.svg" alt="C++" height="40" width="40" />
</a>
<a href="https://www.java.com" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/java/java-original.svg" alt="Java" height="40" width="40" />
</a>
<a href="https://www.python.org" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" height="40" width="40" />
</a>
<a href="https://www.djangoproject.com/" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-original.svg" alt="Django" height="40" width="40" />
</a>
<a href="https://aws.amazon.com" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/amazonwebservices/amazonwebservices-original-wordmark.svg" alt="AWS" height="40" width="40" />
</a>
<a href="https://www.docker.com/" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="Docker" height="40" width="40" />
</a>
<a href="https://www.gnu.org/software/bash/" target="blank">
<img align="center" src="https://www.vectorlogo.zone/logos/gnu_bash/gnu_bash-icon.svg" alt="Bash" height="40" width="40" />
</a>
<a href="https://azure.microsoft.com/en-in/" target="blank">
<img align="center" src="https://www.vectorlogo.zone/logos/microsoft_azure/microsoft_azure-icon.svg" alt="Azure" height="40" width="40" />
</a>
<a href="https://circleci.com" target="blank">
<img align="center" src="https://www.vectorlogo.zone/logos/circleci/circleci-icon.svg" alt="CircleCI" height="40" width="40" />
</a>
<a href="https://nodejs.org" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nodejs/nodejs-original-wordmark.svg" alt="Node.js" height="40" width="40" />
</a>
<a href="https://kafka.apache.org/" target="blank">
<img align="center" src="https://www.vectorlogo.zone/logos/apache_kafka/apache_kafka-icon.svg" alt="Kafka" height="40" width="40" />
</a>
<a href="https://www.rabbitmq.com" target="blank">
<img align="center" src="https://www.vectorlogo.zone/logos/rabbitmq/rabbitmq-icon.svg" alt="RabbitMQ" height="40" width="40" />
</a>
<a href="https://www.nginx.com" target="blank">
<img align="center" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nginx/nginx-original.svg" alt="Nginx" height="40" width="40" />
</a>
<br/>

#### 🔗 Links

[![Email Me](https://img.shields.io/badge/mahboob-black?style=flat&logo=gmail)](mailto:connect.mahboobalam@gmail.com?subject=Hello) 
  <a href="https://twitter.com/imahboob_a" target="_blank">
    <img src="https://img.shields.io/badge/Twitter-05122A?style=flat&logo=twitter&logoColor=white" alt="Twitter">
  </a>
  <a href="https://linkedin.com/in/i-mahboob-alam" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-05122A?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="https://hashnode.com/@imehboob" target="_blank">
    <img src="https://img.shields.io/badge/Hashnode-05122A?style=flat&logo=hashnode&logoColor=white" alt="Hashnode">
  </a>
  <a href="https://medium.com/@imehboob" target="_blank">
    <img src="https://img.shields.io/badge/Medium-05122A?style=flat&logo=medium&logoColor=white" alt="Medium">
  </a>
  <a href="https://dev.to/imahboob_a" target="_blank">
    <img src="https://img.shields.io/badge/Dev.to-05122A?style=flat&logo=dev.to&logoColor=white" alt="Devto">
  </a>
  <a href="https://www.leetcode.com/mahboob-alam" target="_blank">
    <img src="https://img.shields.io/badge/LeetCode-05122A?style=flat&logo=leetcode&logoColor=white" alt="LeetCode">
  </a>
