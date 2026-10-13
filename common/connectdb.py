import pymysql
import redis
from rediscluster import RedisCluster

from common.recordlog import logs
from conf.operationConfig import OperationConfig

conf = OperationConfig()


class ConnectMysql:
    """连接读取MySQL数据库的数据"""

    def __init__(self):
        mysql_conf = {
            'host': conf.get_mysql_conf('host'),
            'port': int(conf.get_mysql_conf('port')),
            'username': conf.get_mysql_conf('username'),
            'password': conf.get_mysql_conf('password'),
            'database': conf.get_mysql_conf('database'),
        }
        try:
            # 连接mysql数据库
            self.conn = pymysql.connect(**mysql_conf, charset='utf8')
            # 游标，cursor=pymysql.cursors.DictCursor将数据库表字段显示，以key-value形式显示
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info("""成功连接到MySQL数据库
            host:{host}
            port:{port}
            db:{database}""".format(**mysql_conf))
        except Exception as e:
            logs.error(e)

    def __del__(self):
        # 关闭连接
        self.conn.close()
        # 关闭游标
        self.cursor.close()

    def close(self):
        """关闭数据库连接"""
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()

    def query(self, sql):
        """查询数据"""
        try:
            # 将sql语句传给mysql服务器执行，只执行不提交，执行的数据只停留在缓冲区中
            self.cursor.execute(sql)
            # 提交事物，把缓冲区的修改永久写入数据库（查询不需要提交）
            self.conn.commit()
            # 获取mysql返回的结果
            res = self.cursor.fetchall()
            return res
        except Exception as e:
            logs.error(e)
        # 无论走上面哪条路都会走finally
        finally:
            # 关闭连接
            self.close()

    def insert(self, sql):
        """新增"""
        pass

    def update(self, sql):
        """修改"""
        pass

    def delete(self, sql):
        """删除"""
        pass


class RedisClient:
    """
    从Redis中读取、设置相关数据
    """

    def __init__(self):
        self.__redis_conf = {
            'host': conf.get_redis_conf('host'),
            'port': int(conf.get_redis_conf('port')),
            'username': conf.get_redis_conf('username'),
            'password': conf.get_redis_conf('password'),
            'db': conf.get_redis_conf('db')
        }
        # redis_nodes_str格式：host:port,host2:port2
        redis_nodes_str = conf.get_redis_conf('startup_nodes')
        self.nodes_list = []
        if redis_nodes_str:
            # 集群操作
            # [host:port,host2:port2]
            nodes_str_list = redis_nodes_str.split(',')
            for node_str in nodes_str_list:
                host,port = node_str.split(":")
                node_data = {'host':host,'port':port}
                self.nodes_list.append(node_data)

            # startup_nodes：集群的格式[{'host':'host','port':'posrt'},{'host2':'host2','port2':'port2'}]
            self.redis_cluster = RedisCluster(startup_nodes=self.nodes_list)
            logs.info(f"连接到redis集群服务，host:{redis_nodes_str}")
        elif self.__redis_conf['host'] and self.__redis_conf['port']:
            # 单节点操作
            try:
                logs.info(f"连接到redis服务器，ip:{self.__redis_conf['host']}")
                # 连接redis
                pool = redis.ConnectionPool(**self.__redis_conf, decode_responses=True, protocol=2)
                self.redis_cluster = redis.Redis(connection_pool=pool)
            except Exception as e:
                logs.error(f"redis连接失败：{e}")

    @classmethod
    def redis_except(self, e):
        if "MOVED" in str(e):
            logs.error(f"请检查Redis是否使用了集群模式或者主从复制的情况，数据被迁移到了另一个redis实力上：{e}")

    def get(self, key):
        """
        获取redis里面的数据
        :param key: redis里面的键
        :return:
        """
        try:
            value = self.redis_cluster.get(key)
            return value
        except Exception as e:
            self.redis_except(e)
            raise

    def set(self,key,value,ex=None):
        """
        设置redis的值
        :param key: 键
        :param value: 需要设置的值
        :param ex: 过期时间，单位s
        :return:
        """
        try:
            self.redis_cluster.set(name=key, value=value, ex=ex)
        except Exception as e:
            self.redis_except(e)


if __name__ == '__main__':
    # conn = ConnectMysql()
    # sql = 'select * from ecs_goods limit 5'
    # print(conn.query(sql))
    redis_conn = RedisClient()
    key = "name"
    res = redis_conn.get(key)
    print(res)
