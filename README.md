<h1>PixivDownloader</h1>
<p>&emsp;A simple script to maintain a collection of illustrations of your favorite anime character.</p>

<h2>Introduction</h2>
<p>
  &emsp;This script implements a web crawler, resource downloader and resource manager. 
  By running a script, you can update and maintain a specific collection of illustrations 
  by setting related parameters such as keywords. 
</p>
<p>
   &emsp;What the does script do can be discribed as follows.
</p>
<p>
   &emsp;First, information of the target illustration is scanned by the crawler 
  (using the pixivpy App-api). Then, a CSV file (illust_data.csv) is used to track 
  all the illustrations that have already been downloaded, which means the illustrations 
  will not be downloaded twice. After that, a download task is generated, and the task 
  is performed by the thread pool. Finally, the CSV file will bem updated and a summary 
  will be displayed.
</p>
<p>
   &emsp;It's worth mentioning that this script simply implements some lightweight features, 
  just as an automated script designed to maintain a small image collection. There 
  are a lot of problems that are not well solved, just use some 'patches' to 
  make the function work for now. 
</p>
<p>
   &emsp;The idea is merely craw and download some illustrations from pixiv, so it is far from being 
  a reliable and decent tool. So, just use it as a simple wheelbarrow.
</p>

<h2>Usage</h2>
    <ul>
        <li>1. Install related dependencies (pixivpy, etc.).</li>
        <li>2. Create a new folder and save the script in it.</li>
        <li>3. Modify the keywords (support multiple keywords). Modify the user name and password 
    used for login (no priority account required).</li>
        <li>4. Run the script. The illustration will be saved in the illustration subfolder.</li>
        <li>5. When you need to update the illustration collection, run the script again.</li>
    </ul>
    
 <h2>Screenshot</h2>
 <img src="https://github.com/CelestialPaler/PixivDownloader/blob/master/screenshot1.jpg" alt="screenshot1" width=900 height="=1080">   
 <img src="https://github.com/CelestialPaler/PixivDownloader/blob/master/screenshot2.jpg" alt="screenshot2" width=900 height="=900">   
      
<h2>About</h2>
<p>Feel free to upload your code and pull a request. More than anything, please share your idea and give me some precious advices. </p>
<img src="https://github.com/CelestialTS/CTHackFramework/blob/master/res/logo.png" alt="Celestial Tech" width=400 height="=100">
<p>For more please check out website: <a href="http://www.tianshicangxie.com">Celestial Tech</a></p>
<p>Copyright © 2019 Celestial Tech</p>
