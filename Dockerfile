FROM alpine

RUN mkdir -p /fashion
WORKDIR /fashion
COPY manage/ /fashion/manage/
COPY mobile/ /fashion/mobile/
COPY static/ /fashion/static/
COPY templates/ /fashion/templates/
COPY config.py /fashion/
COPY fashion.sqlite /fashion/
COPY model.py /fashion/
COPY run.py /fashion/
COPY uploader.py /fashion/
COPY requirements.txt /fashion/
RUN mkdir /lib64
RUN ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --update --no-cache g++ gcc libxslt-dev python3-dev openssl-dev python3 py-pip jpeg-dev zlib-dev jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
EXPOSE 5000
CMD ["python3", "run.py"]