#include "mp2c.h"
void scopeinner();
int a;
int main() {
  a = 20;
  printf("%d", a);
  scopeinner();
  printf("%d", a);
}
void scopeinner() {
  int a;
  a = 10;
  printf("%d", a);
}