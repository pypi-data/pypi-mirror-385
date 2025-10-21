//
// Created by hariharan on 8/8/22.
//

#ifndef BRAHMA_STDIO_H
#define BRAHMA_STDIO_H

#include <brahma/brahma_config.hpp>
/* Internal Headers */
#include <brahma/interceptor.h>
#include <brahma/interface/interface.h>
/* External Headers */
#include <cstdio>
#include <stdexcept>

namespace brahma {
class STDIO : public Interface {
 private:
  static std::shared_ptr<STDIO> my_instance;

 public:
  static std::shared_ptr<STDIO> get_instance() {
    if (my_instance == nullptr) {
      BRAHMA_LOG_INFO("STDIO class not intercepted but used", "");
      my_instance = std::make_shared<STDIO>();
    }
    return my_instance;
  }
  STDIO() : Interface() {}
  virtual ~STDIO(){};
  static int set_instance(std::shared_ptr<STDIO> instance_i) {
    if (instance_i != nullptr) {
      my_instance = instance_i;
      return 0;
    } else {
      BRAHMA_LOG_ERROR("%s instance_i is not set", "STDIO");
      throw std::runtime_error("instance_i is not set");
    }
  }

  template <typename C>
  size_t bind(const char *name, uint16_t priority);


  size_t unbind();

  virtual FILE *fopen(const char *path, const char *mode);
  virtual FILE *fopen64(const char *path, const char *mode);
  virtual int fclose(FILE *fp);
  virtual size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
  virtual size_t fwrite(const void *ptr, size_t size, size_t nmemb,
                        FILE *stream);
  virtual long ftell(FILE *fp);
  virtual int fseek(FILE *stream, long offset, int whence);
  virtual FILE* fdopen(int fd, const char *mode);
  virtual int fileno(FILE *stream);
  virtual FILE* tmpfile(void);
  virtual int fseeko(FILE *stream, off_t offset, int whence);
  virtual off_t ftello(FILE *stream);

  virtual void clearerr(FILE *);
  virtual int feof(FILE *);
  virtual int ferror(FILE *);
  virtual int fflush(FILE *);
  virtual int fgetc(FILE *);
  virtual int fgetpos(FILE *, fpos_t *);
  virtual char* fgets(char *, int, FILE *);
  virtual void flockfile(FILE *);
  virtual int fputc(int, FILE *);
  virtual int fputs(const char *, FILE *);
  virtual FILE* freopen(const char *, const char *, FILE *);
  virtual int fsetpos(FILE *, const fpos_t *);
  virtual int ftrylockfile(FILE *);
  virtual void funlockfile(FILE *);
  virtual int getc(FILE *);
  virtual int getc_unlocked(FILE *);
  virtual int getw(FILE *);
  virtual int pclose(FILE *);
  virtual int putw(int, FILE *);
  virtual void rewind(FILE *);
  virtual int setvbuf(FILE *, char *, int, size_t);
  virtual int ungetc(int, FILE *);

  GOTCHA_MACRO_VAR(fopen)
  GOTCHA_MACRO_VAR(fopen64)
  GOTCHA_MACRO_VAR(fclose)
  GOTCHA_MACRO_VAR(fread)
  GOTCHA_MACRO_VAR(fwrite)
  GOTCHA_MACRO_VAR(ftell)
  GOTCHA_MACRO_VAR(fseek)
  GOTCHA_MACRO_VAR(fdopen)
  GOTCHA_MACRO_VAR(fileno)
  GOTCHA_MACRO_VAR(tmpfile)
  GOTCHA_MACRO_VAR(fseeko)
  GOTCHA_MACRO_VAR(ftello)

  GOTCHA_MACRO_VAR(clearerr)
  GOTCHA_MACRO_VAR(feof)
  GOTCHA_MACRO_VAR(ferror)
  GOTCHA_MACRO_VAR(fflush)
  GOTCHA_MACRO_VAR(fgetc)
  GOTCHA_MACRO_VAR(fgetpos)
  GOTCHA_MACRO_VAR(fgets)
  GOTCHA_MACRO_VAR(flockfile)
  GOTCHA_MACRO_VAR(fprintf)
  GOTCHA_MACRO_VAR(fputc)
  GOTCHA_MACRO_VAR(fputs)
  GOTCHA_MACRO_VAR(freopen)
  GOTCHA_MACRO_VAR(fsetpos)
  GOTCHA_MACRO_VAR(ftrylockfile)
  GOTCHA_MACRO_VAR(funlockfile)
  GOTCHA_MACRO_VAR(getc)
  GOTCHA_MACRO_VAR(getc_unlocked)
  GOTCHA_MACRO_VAR(getopt)
  GOTCHA_MACRO_VAR(gets)
  GOTCHA_MACRO_VAR(getw)
  GOTCHA_MACRO_VAR(pclose)
  GOTCHA_MACRO_VAR(popen)
  GOTCHA_MACRO_VAR(putw)
  GOTCHA_MACRO_VAR(rewind)
  GOTCHA_MACRO_VAR(scanf)
  GOTCHA_MACRO_VAR(setvbuf)
  GOTCHA_MACRO_VAR(snprintf)
  GOTCHA_MACRO_VAR(sprintf)
  GOTCHA_MACRO_VAR(tmpnam)
  GOTCHA_MACRO_VAR(ungetc)

};

}  // namespace brahma
GOTCHA_MACRO_TYPEDEF(fopen, FILE *, (const char *path, const char *mode),
                     (path, mode), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fopen64, FILE *, (const char *path, const char *mode),
                     (path, mode), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fclose, int, (FILE * fp), (fp), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fread, size_t,
                     (void *ptr, size_t size, size_t nmemb, FILE *stream),
                     (ptr, size, nmemb, stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fwrite, size_t,
                     (const void *ptr, size_t size, size_t nmemb, FILE *stream),
                     (ptr, size, nmemb, stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(ftell, long, (FILE * stream), (stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(fseek, int, (FILE * stream, long offset, int whence),
                     (stream, offset, whence), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fdopen, FILE *, (int fd, const char *mode), (fd, mode),
                     brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fileno, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(tmpfile, FILE *, (void), (), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fseeko, int, (FILE * stream, off_t offset, int whence),
                     (stream, offset, whence), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(ftello, off_t, (FILE * stream), (stream), brahma::STDIO)

GOTCHA_MACRO_TYPEDEF(clearerr, void, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(feof, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(ferror, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fflush, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fgetc, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fgetpos, int, (FILE * stream, fpos_t * pos), (stream, pos),
                     brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fgets, char *, (char *s, int size, FILE * stream),
                     (s, size, stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(flockfile, void, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fputc, int, (int c, FILE * stream), (c, stream),
                     brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fputs, int, (const char *s, FILE * stream), (s, stream),
                     brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(freopen, FILE *, (const char *pathname, const char *mode,
                                      FILE * stream),
                     (pathname, mode, stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(fsetpos, int, (FILE * stream, const fpos_t * pos),
                     (stream, pos), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(ftrylockfile, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(funlockfile, void, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(getc, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(getc_unlocked, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(getw, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(pclose, int, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(putw, int, (int w, FILE * stream), (w, stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(rewind, void, (FILE * stream), (stream), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(setvbuf, int, (FILE * stream, char *buf, int mode,
                                    size_t size),
                     (stream, buf, mode, size), brahma::STDIO)
GOTCHA_MACRO_TYPEDEF(ungetc, int, (int c, FILE * stream), (c, stream), brahma::STDIO)


template <typename C>
size_t brahma::STDIO::bind(const char *name, uint16_t priority) {
  GOTCHA_BINDING_MACRO(fopen, STDIO);
  GOTCHA_BINDING_MACRO(fopen64, STDIO);
  GOTCHA_BINDING_MACRO(fclose, STDIO);
  GOTCHA_BINDING_MACRO(fread, STDIO);
  GOTCHA_BINDING_MACRO(fwrite, STDIO);
  GOTCHA_BINDING_MACRO(ftell, STDIO);
  GOTCHA_BINDING_MACRO(fseek, STDIO);
  GOTCHA_BINDING_MACRO(tmpfile, STDIO);
  GOTCHA_BINDING_MACRO(fseeko, STDIO);
  GOTCHA_BINDING_MACRO(ftello, STDIO);
  GOTCHA_BINDING_MACRO(fdopen, STDIO);
  GOTCHA_BINDING_MACRO(fileno, STDIO);

  GOTCHA_BINDING_MACRO(clearerr, STDIO);
  GOTCHA_BINDING_MACRO(feof, STDIO);
  GOTCHA_BINDING_MACRO(ferror, STDIO);
  GOTCHA_BINDING_MACRO(fflush, STDIO);
  GOTCHA_BINDING_MACRO(fgetc, STDIO);
  GOTCHA_BINDING_MACRO(fgetpos, STDIO);
  GOTCHA_BINDING_MACRO(fgets, STDIO);
  GOTCHA_BINDING_MACRO(flockfile, STDIO);
  GOTCHA_BINDING_MACRO(fputc, STDIO);
  GOTCHA_BINDING_MACRO(fputs, STDIO);
  GOTCHA_BINDING_MACRO(freopen, STDIO);
  GOTCHA_BINDING_MACRO(fsetpos, STDIO);
  GOTCHA_BINDING_MACRO(ftrylockfile, STDIO);
  GOTCHA_BINDING_MACRO(funlockfile, STDIO);
  GOTCHA_BINDING_MACRO(getc, STDIO);
  GOTCHA_BINDING_MACRO(getc_unlocked, STDIO);
  GOTCHA_BINDING_MACRO(getw, STDIO);
  GOTCHA_BINDING_MACRO(pclose, STDIO);
  GOTCHA_BINDING_MACRO(putw, STDIO);
  GOTCHA_BINDING_MACRO(rewind, STDIO);
  GOTCHA_BINDING_MACRO(setvbuf, STDIO);
  GOTCHA_BINDING_MACRO(ungetc, STDIO);

  num_bindings = bindings.size();
  if (num_bindings > 0) {
    sprintf(tool_name, "%s_stdio", name);
    gotcha_binding_t *raw_bindings = bindings.data();
    gotcha_wrap(raw_bindings, num_bindings, tool_name);
    bind_priority = priority;
    gotcha_set_priority(tool_name, priority);
  }
  return num_bindings;
}
#endif  // BRAHMA_STDIO_H
