One elementary observation is an array of centroids

There is a problem with mismatching of centroids detection and how these centroids 
will be located on the screen. Per example, we have a screen, in ideal variant
we open browser make a screen of web page detect centroids and change nothing,
but if we open console or change the resolution, or wrap browser centroids will change the locations.
The first screen is the how centroids were detected on a web page with open console. 
The second is how the web components detected on the screenshot by Yolo.
As we can see that the accuracy of detection is very high, but the shift on real web page is too big. 


If we detect centroids then observation should be the tuple of centroids for actor-critic.
Why we don't use centroids tuple? Because the amount of the centroids is changing everytime.
So we need to detect probability for each element and get probabilites for centroids.

How to choose the ...

The important mark which we should to check is when we detect the centroids better: 1) when we
use just common screen or 2) when we use prepared screen or thresh imaged or 3) when we use gray image;

When we type it is necessary to check if we can to type or not. If element is not textarea or inputtype, there is
no necessity to type.

The problem with saving text in json file is that we need to keep centroid coordinates and data. But the centroids
change everytime.And we can't hardcode it. Centroids are not changing. They keep to be in the same place. But we
need somehow create the json mathcing tables coordinates - data. It is a problem to do it by hands because we need
to see coordinates on every page.

The second problem is transition between pages with different urls. Because when we achieve of terminal state, we
should reset environment till the learning is continueing. 

Important: the dropdown fields where we can choose day, year or some list data recognised as
input element.


If to solve the problem with text by stopping of program execution and waiting when user enter
data! The first what we should do? We should get web element from point. For this we should
to understand what dom element the js back: the first, the last which met in tree? For this, 
we text the code that will mark by red border our elements. Here we can see, if our centroids
counteg wrong we will get another web element, what can be considered as possible mistake or 
vulnerability. As you can see from the pic "elements from point", js back the last element
from point, that is statisfied us. Important: The idea doesn't work because selenium can't to 
transfer control to user. But we can set timer and put all data. But if the cycle of training 
is 100 times, to put all data 100 times is not suitable. The idea is to put data only on certain
steps of cycle, for each 20 or for each 30 per example. 

Important: why you declined pyautogui? Because you should make a screen of body, but pyautogui 
is strictly connected with coordinates. 

Important: very big problems appears with modal windows. The first: selenium doesn't see a modal
window and acts like it doesn't exist. The second: we need to create smth that will be detect
that modal window is opened. When we detect that it is modal window, we can cathc it and act
with it another way. The idea of catching modal windows is to set timer which everytime will
wait for modal dialog and catch it when it open. it doesn't work. Just need to solve one problem
is to understand when modal dialog is appear. Because of json file, we should now on what window
does it appear.


Цикл по центроидам не работает так как последовательность прохождения центроидов всегда
одинаковая, а она должна меняться.
The circle for centroids with the same order doesn't work, because if the order of centroids
doesn't change, then algorithm never find the state when we type credentials and press
Sign in button. The agent always will repeat the same actions. The problem were solved by
shuffle of centroids before each iteration.

The problem of text and coordinates is: sometimes the agent doesn't type text in corresponding
coordinates. The first: the cause can be in the checking of the html elements on the equality.
The second: problem is not in the detection of centroids.
The third:need to check if we don't check the elements on similiraty.
If we don't check the similarity the problems sometimes deliminate
On each step we get the different coordinates of centroids.
The problem was decided by find of nearest coordinates.

The autofill passwords settings should be turn off in Google Chrome.

To reset the environment after login we open new tab and close the previous.

