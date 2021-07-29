centroids = [[960, 567], [504, 260], [502, 622], [573, 625], [436, 625],
    [965, 434], [539, 626], [470, 625], [164, 28], [178, 670],
    [342, 554], [986, 243], [504, 625], [964, 178], [970, 368],
    [967, 123], [963, 489], [1064, 27], [1057, 585], [862, 584],
    [426, 347], [880, 245], [436, 25], [963, 585]]

const myCanvas = document.createElement('canvas');
document.body.appendChild(myCanvas);
myCanvas.id = 'canvas';
myCanvas.style.position = 'absolute';
myCanvas.style.left = '0px';
myCanvas.style.top = '0px';
myCanvas.width = window.innerWidth;
myCanvas.height = window.innerHeight;
const ctx = myCanvas.getContext('2d');

for(let i = 0; i < centroids.length; i++) {
    let x = centroids[i][0];
    let y = centroids[i][1];
    ctx.fillStyle = '#2980b9';
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, 2 * Math.PI);
    ctx.fill();
}
