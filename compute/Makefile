CFLAGS += -Wall -Wextra -Werror -std=c11 -march=native -flto=auto
ifeq ($(FAST),true)
  CFLAGS += -Ofast
else
  CFLAGS += -O3
endif

ifeq ($(AVX2),false)
else
  CFLAGS += -DUSE_AVX2
endif

ifeq ($(DEBUG),true)
  CFLAGS += -g -DVERBOSE
else ifeq ($(VERBOSE),true)
  CFLAGS += -DVERBOSE
endif

countBoards: countBoards.c
	$(CC) "$@.c" -o "$@" $(CFLAGS)

.PHONY: clean
clean:
	@rm -fv countBoards
