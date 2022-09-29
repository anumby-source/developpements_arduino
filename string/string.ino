
String a = "0123456789012345678901234567890123456789";



void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);

  Serial.println("...");
  Serial.println("...");
  Serial.println("...");

  int len = a.length();
  int increment = 6;
  int start = 0;
  int end = 0;

  while (len > 0){
    char chars[increment + 1];
    int sub = increment;
    if (len <= increment) sub = len;
    end = start + sub;
    String s = a.substring(start, end);
    s.toCharArray(chars, sub+1);

    Serial.print("web_page> len=" + String(len));
    Serial.print(" [" + String(start) + ":" + String(end) + "]");
    Serial.print(" chars = [");
    Serial.print(chars);
    Serial.print("]");
    Serial.println(" a= [" + s + "]");

    len -= sub;
    start = end;
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
