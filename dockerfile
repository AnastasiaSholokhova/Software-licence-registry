FROM python:3.11.9-slim
ENV PATH=$PATH:C:/Users/Anastasia/anaconda3/Library/bin
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=12345
ENV POSTGRES_DB=Users
ENV POSTGRES_DB2=software_licences



COPY requirements.txt /

RUN pip3 install --upgrade pip

RUN pip3 install -r /requirements.txt

RUN pip install waitress

COPY . /app

WORKDIR /app

EXPOSE 5000

CMD ["waitress-serve", "--listen=:5000", "app:app"]