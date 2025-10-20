CC := gcc
CFLAGS = -Wall -g
SOURCES = main.c \
  utils.c \
    helper.c

all: $(TARGET)
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f *.o
