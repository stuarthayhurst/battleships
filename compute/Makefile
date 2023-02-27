CFLAGS := -Wall -Wextra -Werror -march=native -flto=auto
ifeq ($(FAST),true)
  CFLAGS += -Ofast
else
  CFLAGS += -O3
endif

countBoards: countBoards.c
	$(CC) "$@.c" -o "$@" $(CFLAGS)

.PHONY: clean
clean:
	@rm -fv countBoards
