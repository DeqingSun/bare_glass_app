
void setup() {
  frameRate(1);
}
void draw() {
  String[] lines = loadStrings("http://bareboneglass.appspot.com/simplepage");
  println(lines[0]);
  if (lines[0].toLowerCase().indexOf("on")>=0) background(255);
  if (lines[0].toLowerCase().indexOf("off")>=0) background(0);
  
}

