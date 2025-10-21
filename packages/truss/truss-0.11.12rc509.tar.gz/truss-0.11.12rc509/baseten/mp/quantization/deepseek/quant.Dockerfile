FROM axolotlai/axolotl:main-20250818-py3.11-cu126-2.7.1

RUN pip install --upgrade pip
RUN pip install nvidia-modelopt[all]
RUN apt install -y tmux

WORKDIR /quant
COPY . .

CMD ["sleep", "infinity"]