import pandas as pd
import argparse
import settings
import os
from py2neo import Graph, Node, Relationship, authenticate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('game', nargs=1, type=str)
    args = parser.parse_args()
    vids = VideoSequencesCreation(args.game[0])
    vids.make_sequence()
    #images = VideoProcessing()

class VideoSequencesCreation:
    def __init__(self, game):
        self.game = game
        self.video_ids = []
        self.ratings = []
        self.seq_ids = []

    def make_sequence(self):
        authenticate(settings.NeoHost, settings.NeoLog, settings.NeoPass)
        graph = Graph("{0}/db/data/".format(settings.NeoHost))
        query = """MATCH (start:Video)-[:Jaccard*5..10]->(sequence:Video) 
        WHERE start<>sequence MATCH p=shortestPath((start:Video)-[:Jaccard*]->(sequence:Video)) 
        WHERE NONE (n IN nodes(p) WHERE size(filter(x IN nodes(p) WHERE n = x))> 1)  
        RETURN EXTRACT(n IN NODES(p)|[n.id, n.rating]) LIMIT 100000"""
   
        r1 = graph.run(query).data()
        k = 0
        for i in r1:
            #print(i.values)
            for video in i['EXTRACT(n IN NODES(p)|[n.id, n.rating])']:
                 #print(video)
                 self.seq_ids.append(k)
                 self.video_ids.append(video[0])
                 self.ratings.append(video[1])
            k+=1
        data = {'sequence': self.seq_ids, 'video': self.video_ids, 'rating': self.ratings}
        df = pd.DataFrame(data)
        df = df[pd.notnull(df['video'])]
        print(df)
        dz = df.groupby('sequence')['rating'].std()
        print(dz)

        path = '{0}/{1}/'.format(settings.VideosDirPath, self.game)
        if not os.path.exists(path):
            os.makedirs(path)
        file_name = '{0}/sequences.csv'.format(path)
        df.to_csv(file_name, encoding='utf-8')
        summary_data = '{0}/summary.csv'.format(path)
        dz.to_csv(summary_data, encoding='utf-8')
        return



if __name__ == "__main__":
    main()
