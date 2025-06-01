CFLAGS += -Wall -Wextra -Werror -Wpedantic -std=c11 -O3

ifndef ARCH
  CFLAGS += -march=native
else
  CFLAGS += -march=$(ARCH)
endif

ifeq ($(AVX512),false)
else
  CFLAGS += -DUSE_AVX512
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
