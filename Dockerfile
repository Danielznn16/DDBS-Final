FROM python:3.8
WORKDIR /usr/src/app
COPY backend .
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
RUN chmod +x start.sh
CMD ["./start.sh"]