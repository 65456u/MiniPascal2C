#include "stdio.h"
int gcd(int a, int b);
int x;
int y;
int main() {
  scanf("%d%d", &x, &y);
  printf("%d", gcd(x, y));
}
int gcd(int a, int b) {
  int _gcd;
  if (b == 0) {
    _gcd = a;
  } else {
    _gcd = gcd(b, a % b);
  };
  return _gcd;
}